"""脚本实际解析、Hydra 装配、单双卡及退休入口。"""

import shlex
import subprocess

import pytest
from bash_fixture import bash as bash_fixture
from formal_config_helpers import ROOT, compose_argv
from omegaconf import OmegaConf

bash = bash_fixture

BASE = [
    "--data-dir",
    "data/beauty spaced",
    "--dataset",
    "beauty",
    "--semantic-id-path",
    "wandb://fixture/GRID/sid?role=semantic_id&file=merged_predictions_tensor.pt",
    "--embedding-path",
    "content.pt",
    "--seed",
    "42",
]


def launch(bash, script, args, prefix=""):
    command = 'uv() { printf "%s\\n" "$@"; }; export -f uv; ' + prefix + "bash " + shlex.join([script, *BASE, *args])
    return subprocess.run([bash], input=command, cwd=ROOT, text=True, capture_output=True)


@pytest.mark.parametrize("variant", [None, "no_mixture", "no_residual", "no_joint_ce", "fixed_alpha_one"])
@pytest.mark.parametrize("stage", ["train", "inference"])
@pytest.mark.parametrize("equals", [False, True])
def test_actual_script_composes_v2_single_or_dual_card_notes_and_overrides(bash, variant, stage, equals):
    notes = 'v2 "joint view", A=B'
    args = ["--devices", "[0,1]" if stage == "train" else "[0]"]
    args += ["--notes=" + notes] if equals else ["--notes", notes]
    if variant:
        args += ["--variant", variant]
    if stage == "inference":
        args += [
            "--checkpoint",
            "wandb://fixture/GRID/own?role=checkpoint&alias=v0&file=own.ckpt",
            "--checkpoint-sha256",
            "8" * 64,
        ]
    r = launch(bash, "copmrec_" + ("ablation_" if variant else "") + stage + ".sh", args)
    assert r.returncode == 0, r.stderr
    cfg = compose_argv(r.stdout.splitlines())
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert cfg.copmrec_version == cfg.implementation_version == cfg.method_version == "v2"
    assert cfg.logger.wandb.notes == notes
    assert cfg.native_view_ce is None and cfg.training_objective.native_view_computed is False
    assert not cfg.inference_history_exclusion
    assert "--dry-run" not in r.stdout.splitlines()
    assert ("--nproc_per_node=2" in r.stdout.splitlines()) == (stage == "train")
    if stage == "train":
        assert cfg.trainer.root.max_steps == 50000 and cfg.data.train_dataloader.batch_size_per_device == 128
        assert cfg.model.root.prediction_mode == cfg.model.root.evaluation_mode == "dense"
    else:
        assert cfg.checkpoint_sha256 == "8" * 64 and cfg.data.predict_dataloader.data_folder.endswith("/testing")
        assert cfg.model.root.prediction_mode == "hybrid" and cfg.model.root.evaluation_mode == "dense"
        metadata = cfg.callbacks.wandb_artifact_writer.metadata
        assert metadata.deployment_contract.mode == "hybrid"
        assert metadata.deployment_contract.candidate_pool == "beam_plus_all_cold"
        assert metadata.deployment_contract.generation_candidates == 20
        assert metadata.history_eligibility_contract.score_rule == "unchanged_candidate_joint_logits"
    if variant:
        assert cfg.model.root.variant == variant and cfg.formal_release.variant == variant
        assert cfg.training_objective.joint_catalog_ce == int(variant != "no_joint_ce")
        assert cfg.training_objective.mixture_nll == int(variant != "no_mixture")
        policy = {"no_mixture": "frozen_0.5", "fixed_alpha_one": "frozen_1"}.get(variant, "learned")
        fixed_alpha = {"no_mixture": 0.5, "fixed_alpha_one": 1.0}.get(variant)
        assert cfg.alpha_policy == policy and cfg.fixed_mixture_alpha == fixed_alpha
        writer = cfg.callbacks.wandb_checkpoint_writer if stage == "train" else cfg.callbacks.wandb_artifact_writer
        assert writer.metadata.alpha_policy == policy
        assert writer.metadata.fixed_mixture_alpha == fixed_alpha
        assert writer.metadata.ablation_variant == variant
        # 基础兼容参数不是训练后 gate 的取值；有效策略另行记录。
        assert cfg.model.root.content_mixture_alpha == 0.5
        if stage == "inference":
            assert writer.metadata.deployment_contract.alpha_policy == policy
            assert writer.metadata.deployment_contract.alpha_source == (
                "checkpoint" if policy == "learned" else "fixed"
            )
            assert writer.metadata.deployment_contract.fixed_mixture_alpha == fixed_alpha


@pytest.mark.parametrize("variant", [None, "no_mixture", "no_residual", "no_joint_ce", "fixed_alpha_one"])
@pytest.mark.parametrize(
    "mode_args", [["--deployment=dense"], ["--deployment", "dense"], ["model.root.prediction_mode=dense"]]
)
def test_dense_override_changes_actual_deployment_metadata_and_notes(bash, variant, mode_args):
    args = ["--devices", "[0]", "--checkpoint", "own.ckpt", "--checkpoint-sha256", "8" * 64, *mode_args]
    if variant:
        args += ["--variant", variant]
    r = launch(bash, "copmrec_" + ("ablation_" if variant else "") + "inference.sh", args)
    assert r.returncode == 0, r.stderr
    cfg = compose_argv(r.stdout.splitlines())
    metadata = cfg.callbacks.wandb_artifact_writer.metadata
    assert cfg.model.root.prediction_mode == cfg.model.root.evaluation_mode == "dense"
    assert metadata.deployment_contract.mode == "dense"
    assert metadata.deployment_contract.candidate_pool == "all_catalog"
    assert metadata.history_eligibility_contract.protocol == "copmrec-final-history-exclusion-off-v1"
    assert metadata.history_eligibility_contract.score_rule == "unchanged_full_catalog_logits"
    assert "部署=dense" in cfg.logger.wandb.notes
    assert cfg.task_name.endswith("_dense_inference")


def test_deployment_option_preserves_late_override_priority(bash):
    r = launch(
        bash,
        "copmrec_inference.sh",
        [
            "--devices",
            "[0]",
            "--checkpoint",
            "own.ckpt",
            "--checkpoint-sha256",
            "8" * 64,
            "--deployment",
            "dense",
            "model.root.prediction_mode=hybrid",
        ],
    )
    assert r.returncode == 0, r.stderr
    cfg = compose_argv(r.stdout.splitlines())
    assert cfg.model.root.prediction_mode == cfg.deployment_contract.mode == "hybrid"


@pytest.mark.parametrize("stage", ["train", "inference"])
def test_fixed_alpha_script_explicit_dry_run_and_late_hydra_override(bash, stage):
    args = [
        "--variant=fixed_alpha_one",
        "--devices",
        "[0,1]" if stage == "train" else "[0]",
        "--dry-run",
        "--notes=default notes",
        "logger.wandb.notes=override wins",
        "+trainer.root.limit_val_batches=2",
    ]
    if stage == "inference":
        args += ["--checkpoint", "fixed_alpha_one own.ckpt", "--checkpoint-sha256=" + "8" * 64]
    r = launch(bash, f"copmrec_ablation_{stage}.sh", args)
    assert r.returncode == 0, r.stderr
    cfg = compose_argv(r.stdout.splitlines())
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert "--dry-run" in r.stdout.splitlines()
    assert cfg.logger.wandb.notes == "override wins"
    assert cfg.trainer.root.limit_val_batches == 2
    assert cfg.ablation_variant == "fixed_alpha_one"
    assert (
        cfg.training_objective.sid_ce
        == cfg.training_objective.joint_catalog_ce
        == cfg.training_objective.mixture_nll
        == 1.0
    )
    assert cfg.alpha_policy == "frozen_1" and cfg.fixed_mixture_alpha == 1.0


@pytest.mark.parametrize(
    "analysis,variant", [("hits", "full"), ("residual", "full"), ("prefix", "full"), ("prefix", "no_mixture")]
)
def test_diagnosis_uses_single_card_Trainer_test_and_v2(bash, analysis, variant):
    args = [
        "--analysis",
        analysis,
        "--variant",
        variant,
        "--devices",
        "[0]",
        "--dry-run",
        "--notes=quoted analysis",
        "logger.wandb.notes=override wins",
    ]
    if analysis != "hits":
        args += ["--checkpoint", "own.ckpt", "--checkpoint-sha256", "8" * 64]
    r = launch(bash, "copmrec_diagnosis.sh", args)
    assert r.returncode == 0, r.stderr
    cfg = compose_argv(r.stdout.splitlines())
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert cfg.run_mode == "analysis" and cfg.method_version == "v2"
    assert cfg.model.root.exclude_history is False and cfg.logger.wandb.notes == "override wins"
    assert "--dry-run" in r.stdout and "--nproc_per_node=2" not in r.stdout
    assert cfg.diagnosis_backbone.root.prediction_mode == "dense"
    if analysis == "hits":
        assert cfg.expected_deployment_protocol == cfg.evaluation_protocol == "copmrec-hybrid-deployment-v1"
        assert cfg.model.root.prediction_bundles.expected_deployment_protocol == cfg.evaluation_protocol
    else:
        assert cfg.expected_deployment_protocol is None
        assert cfg.evaluation_protocol == "copmrec-v2-ablation-20261009-v1"


def test_legacy_dense_hits_can_be_requested_explicitly(bash):
    r = launch(bash, "copmrec_diagnosis.sh", ["--analysis", "hits", "--devices", "[0]", "hits_deployment_mode=dense"])
    assert r.returncode == 0, r.stderr
    cfg = compose_argv(r.stdout.splitlines())
    assert cfg.expected_deployment_protocol is None
    assert cfg.evaluation_protocol == "copmrec-v2-ablation-20261009-v1"


@pytest.mark.parametrize(
    "script,args,prefix",
    [
        ("copmrec_train.sh", ["--devices", "[0,1]", "--checkpoint", "old.ckpt"], ""),
        ("copmrec_train.sh", ["--devices", "[0,1]", "--notes", ""], ""),
        ("copmrec_train.sh", ["--devices", "[0,1]"], "export NPROC_PER_NODE=1; "),
        ("copmrec_inference.sh", ["--devices", "[0]", "--checkpoint", "own.ckpt"], ""),
        ("copmrec_inference.sh", ["--devices", "[0]", "--checkpoint-sha256=bad"], ""),
        ("copmrec_inference.sh", ["--checkpoint-sha256=" + "8" * 64, "--deployment="], ""),
        ("copmrec_inference.sh", ["--checkpoint-sha256=" + "8" * 64, "--deployment", ""], ""),
        ("copmrec_inference.sh", ["--checkpoint-sha256=" + "8" * 64, "--deployment=generative"], ""),
        (
            "copmrec_inference.sh",
            ["--devices", "[0]", "--checkpoint", "own.ckpt", "--checkpoint-sha256", "8" * 64],
            "export NPROC_PER_NODE=2; ",
        ),
        ("copmrec_ablation_train.sh", ["--variant=no_native"], ""),
        ("copmrec_ablation_train.sh", ["--variant="], ""),
        ("copmrec_ablation_train.sh", ["--variant", ""], ""),
        ("copmrec_ablation_train.sh", ["--variant", "fixed_alpha_one", "--notes="], ""),
        ("copmrec_ablation_train.sh", ["--variant=fixed_alpha_one", "--notes", ""], ""),
        ("copmrec_ablation_train.sh", ["--variant=fixed_alpha_one", ""], ""),
        ("copmrec_ablation_inference.sh", ["--variant=fixed_alpha_one", "--checkpoint-sha256="], ""),
        ("copmrec_ablation_inference.sh", ["--variant=fixed_alpha_one", "--checkpoint-sha256=bad"], ""),
    ],
)
def test_reject_invalid_inputs_before_uv(bash, script, args, prefix):
    r = launch(bash, script, args, prefix)
    assert r.returncode == 2 and "src.main" not in r.stdout


def test_shell_syntax_and_only_current_experiments(bash):
    for script in ROOT.glob("copmrec*.sh"):
        r = subprocess.run([bash, "-n", str(script)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    assert {p.stem for p in (ROOT / "configs/experiment").glob("copmrec*.yaml")} == {
        "copmrec_train",
        "copmrec_inference",
        "copmrec_ablation_train",
        "copmrec_ablation_inference",
        "copmrec_diagnosis",
    }
