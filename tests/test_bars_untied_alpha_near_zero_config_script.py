"""临时 Untied 近零 alpha 初始化的配置与脚本契约。"""

import subprocess

import pytest
from bash_fixture import bash as bash_fixture
from formal_config_helpers import ROOT
from omegaconf import OmegaConf
from test_bars_v2_config_script import compose_argv, launch

bash = bash_fixture

VARIANT = "untied_alpha_near_zero"


@pytest.mark.parametrize("stage", ["train", "inference"])
@pytest.mark.parametrize("equals", [False, True])
@pytest.mark.parametrize("dry_run", [False, True])
def test_near_zero_variant_composes_learned_alpha_and_untied_identity(bash, stage, equals, dry_run):
    notes = 'temporary "alpha=0.0001", W&B only; path with spaces'
    args = ["--variant=" + VARIANT] if equals else ["--variant", VARIANT]
    args += ["--devices", "[0,1]" if stage == "train" else "[0]"]
    args += ["--notes=" + notes] if equals else ["--notes", notes]
    group = "temporary bars alpha near zero beauty seed42"
    args += ["--group=" + group] if equals else ["--group", group]
    if dry_run:
        args += ["--dry-run"]
    task_name = "bars_temp_beauty_seed42_untied_alpha_near_zero_" + stage
    display = "temporary learned alpha from 0.0001"
    args += ["task_name=" + task_name, f'logger.wandb.name="{display}"', "model.root.generation_candidates=17"]
    if stage == "inference":
        args += ["--checkpoint", "own near zero.ckpt", "--checkpoint-sha256", "8" * 64]
    result = launch(bash, f"bars_ablation_{stage}.sh", args)
    assert result.returncode == 0, result.stderr
    argv = result.stdout.splitlines()
    cfg = compose_argv(argv)
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert ("--dry-run" in argv) is dry_run
    assert cfg.model.root.variant == cfg.formal_release.variant == cfg.ablation_variant == VARIANT
    alpha = cfg.model.ablation_alpha[VARIANT]
    assert alpha.policy == cfg.alpha_policy == "learned"
    assert alpha.source == "checkpoint"
    assert alpha.fixed_mixture_alpha is cfg.fixed_mixture_alpha is None
    assert alpha.initial_alpha == 0.0001 and alpha.parameterization == "sigmoid_logit"
    assert cfg.model.root.content_mixture_alpha == 0.5
    assert cfg.residual_sharing == "untied_history_catalog" and cfg.residual_table_count == 2
    assert cfg.residual_comparison_protocol == "temporary-bars-untied-alpha-near-zero-v1"
    assert (
        cfg.training_objective.sid_ce
        == cfg.training_objective.joint_catalog_ce
        == cfg.training_objective.mixture_nll
        == 1.0
    )
    assert cfg.group == cfg.logger.wandb.group == group
    assert cfg.logger.wandb.name == display and cfg.logger.wandb.notes == notes
    assert cfg.model.root.generation_candidates == 17
    writer = cfg.callbacks.wandb_checkpoint_writer if stage == "train" else cfg.callbacks.wandb_artifact_writer
    assert writer.task_name == cfg.task_name == task_name
    assert writer.artifact_name.startswith(task_name + "-")
    assert writer.metadata.ablation_variant == VARIANT
    assert writer.metadata.alpha_policy == "learned" and writer.metadata.fixed_mixture_alpha is None
    assert writer.metadata.residual_sharing == "untied_history_catalog" and writer.metadata.residual_table_count == 2
    assert writer.metadata.residual_comparison_protocol == "temporary-bars-untied-alpha-near-zero-v1"
    if stage == "train":
        assert cfg.ckpt_path is None and cfg.trainer.root.max_steps == 50000
        assert cfg.trainer.root.val_check_interval == 500 and cfg.trainer.root.precision == "32-true"
        assert cfg.data.train_dataloader.batch_size_per_device == 128
        assert "--nproc_per_node=2" in argv
    else:
        assert cfg.checkpoint_sha256 == "8" * 64
        assert writer.metadata.deployment_contract.alpha_policy == "learned"
        assert writer.metadata.deployment_contract.alpha_source == "checkpoint"
        assert writer.metadata.deployment_contract.fixed_mixture_alpha is None


@pytest.mark.parametrize("stage", ["train", "inference"])
def test_near_zero_script_preserves_late_overrides(bash, stage):
    args = [
        "--variant=" + VARIANT,
        "--devices",
        "[0,1]" if stage == "train" else "[0]",
        "--notes=earlier notes",
        "--group=earlier group",
        'logger.wandb.notes="override notes"',
        'group="override group"',
        "+trainer.root.limit_val_batches=2",
    ]
    if stage == "inference":
        args += ["--checkpoint", "own.ckpt", "--checkpoint-sha256=" + "8" * 64]
    result = launch(bash, f"bars_ablation_{stage}.sh", args)
    assert result.returncode == 0, result.stderr
    cfg = compose_argv(result.stdout.splitlines())
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert cfg.logger.wandb.notes == "override notes"
    assert cfg.group == cfg.logger.wandb.group == "override group"
    assert cfg.trainer.root.limit_val_batches == 2
    assert cfg.ablation_variant == VARIANT


@pytest.mark.parametrize(
    "invalid",
    [["--notes="], ["--notes", ""], ["--group="], ["--group", ""], [""], ["--variant=unknown"]],
)
def test_near_zero_rejects_invalid_values_before_launch(bash, invalid):
    result = launch(bash, "bars_ablation_train.sh", ["--variant=" + VARIANT, *invalid])
    assert result.returncode == 2 and "src.main" not in result.stdout


@pytest.mark.parametrize("invalid", [["--checkpoint-sha256="], ["--checkpoint-sha256=bad"]])
def test_near_zero_inference_rejects_invalid_checkpoint_identity(bash, invalid):
    result = launch(
        bash,
        "bars_ablation_inference.sh",
        ["--variant=" + VARIANT, "--checkpoint", "own.ckpt", *invalid],
    )
    assert result.returncode == 2 and "src.main" not in result.stdout


def test_near_zero_entry_scripts_have_valid_shell_syntax(bash):
    for name in ("bars_m3_common.sh", "bars_ablation_train.sh", "bars_ablation_inference.sh"):
        result = subprocess.run([bash, "-n", str(ROOT / name)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
