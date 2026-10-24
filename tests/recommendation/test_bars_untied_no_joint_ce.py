"""Untied 直接目录监督移除的匹配条件、双表优化与独立恢复。"""

import copy
import shlex
import subprocess
from pathlib import Path

import pytest
import torch
from bars_fixtures import bars, snapshot
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf
from test_bars_untied_residual import checkpoint, optimizers, residual_weights, update
from test_liger import batch

import src.utils.hydra_resolvers  # noqa: F401
from src.recommendation.bars.ablation import TRAINING_VARIANTS, VARIANTS

VARIANT = "untied_no_joint_ce"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def saved_no_joint_ce():
    return snapshot(VARIANT, updates=2)[1]


def test_removal_preserves_untied_initialization_rng_and_all_other_loss_terms():
    options = dict(initialization_seed=200, dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(200)
    full = bars("untied_residual", **options)
    full_rng = torch.get_rng_state()
    torch.manual_seed(200)
    removed = bars(VARIANT, **options)
    assert torch.equal(torch.get_rng_state(), full_rng)
    torch.testing.assert_close(removed.state_dict(), full.state_dict(), rtol=0, atol=0)
    catalog, history = residual_weights(removed)
    assert catalog.data_ptr() != history.data_ptr()
    assert not torch.count_nonzero(catalog) and not torch.count_nonzero(history)
    assert removed.content_projection is not None

    inputs, labels = batch()
    torch.manual_seed(100)
    full_values = full.losses(inputs, labels.target_ids, training=True)
    full_rng = torch.get_rng_state()
    torch.manual_seed(100)
    values = removed.losses(inputs, labels.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), full_rng)
    for name in ("sid_loss", "content_loss", "mixture_loss", "mixture_alpha"):
        torch.testing.assert_close(values[name], full_values[name], rtol=0, atol=0)
    torch.testing.assert_close(values["loss"], values["sid_loss"] + values["mixture_loss"], rtol=0, atol=0)
    assert removed.dynamic_gate.bias.requires_grad
    values["loss"].backward()
    assert removed.dynamic_gate.bias.grad.abs().sum() > 0
    for weight in (catalog, history):
        assert weight.grad is not None and torch.isfinite(weight.grad).all()
        assert weight.grad[removed.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight.grad[~removed.seen_mask])


def test_both_roles_keep_residual_lr_and_zero_cold_rows_after_updates():
    actual = bars(VARIANT)
    optimizer, scheduler = optimizers(actual)
    weights = residual_weights(actual)
    assert len(optimizer.param_groups) == 2
    assert [group["initial_lr"] for group in optimizer.param_groups] == [0.0003, 0.002]
    assert len(optimizer.param_groups[1]["params"]) == 2
    for weight in weights:
        assert any(parameter is weight for parameter in optimizer.param_groups[1]["params"])
        assert all(parameter is not weight for parameter in optimizer.param_groups[0]["params"])
    for _ in range(3):
        update(actual, optimizer, scheduler)
    for weight in weights:
        assert weight[actual.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight[~actual.seen_mask])
        assert optimizer.state[weight]["step"].item() == 3
        assert optimizer.state[weight]["exp_avg"].abs().sum() > 0


def test_identity_declares_only_the_joint_ce_removal_and_legacy_variants_do_not_change():
    assert VARIANTS == ("no_mixture", "no_residual", "no_joint_ce")
    assert VARIANT in TRAINING_VARIANTS
    actual = bars(VARIANT)
    assert actual.ablation_contract == dict(
        protocol="copmrec-v2-ablation-20261009-v1",
        base_release="copmrec-v2",
        variant=VARIANT,
        loss_weights=dict(sid_ce=1, joint_catalog_ce=0, mixture_nll=1),
        alpha_policy="learned",
        residual_mode="untied_history_catalog",
    )
    assert actual.residual_contract == bars("untied_residual").residual_contract
    assert actual.formal_release["variant"] == VARIANT
    assert actual.unified_scratch_contract["m3_ablation"] == actual.ablation_contract
    for variant in (*VARIANTS, "fixed_alpha_one", "untied_residual"):
        original = bars(variant)
        assert original.ablation_contract == dict(
            protocol="copmrec-v2-ablation-20261009-v1",
            base_release="copmrec-v2",
            variant=variant,
            loss_weights=dict(
                sid_ce=1,
                joint_catalog_ce=int(variant != "no_joint_ce"),
                mixture_nll=int(variant != "no_mixture"),
            ),
            alpha_policy={"no_mixture": "frozen_0.5", "fixed_alpha_one": "frozen_1"}.get(variant, "learned"),
            residual_mode={"no_residual": "frozen_zero_both", "untied_residual": "untied_history_catalog"}.get(
                variant, "shared_history_catalog"
            ),
        )


def test_own_complete_restore_preserves_next_optimizer_and_scheduler_update(saved_no_joint_ce):
    actual, saved = snapshot(VARIANT, updates=2)
    optimizer, scheduler = optimizers(actual)
    optimizer.load_state_dict(copy.deepcopy(saved["optimizer_states"][0]))
    scheduler.load_state_dict(copy.deepcopy(saved["lr_schedulers"][0]))
    restored = bars(VARIANT)
    restored.on_load_checkpoint(saved_no_joint_ce)
    restored.load_state_dict(saved_no_joint_ce["state_dict"], strict=True)
    restored_optimizer, restored_scheduler = optimizers(restored)
    restored_optimizer.load_state_dict(copy.deepcopy(saved_no_joint_ce["optimizer_states"][0]))
    restored_scheduler.load_state_dict(copy.deepcopy(saved_no_joint_ce["lr_schedulers"][0]))
    assert restored.restored_step == 2
    update(actual, optimizer, scheduler)
    update(restored, restored_optimizer, restored_scheduler)
    torch.testing.assert_close(restored.state_dict(), actual.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_optimizer.state_dict(), optimizer.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_scheduler.state_dict(), scheduler.state_dict(), rtol=0, atol=0)
    bars(VARIANT).on_load_checkpoint(checkpoint(restored, restored_optimizer, restored_scheduler, 3))


@pytest.mark.parametrize("other", [None, "no_joint_ce", "untied_residual"])
def test_restore_rejects_shared_shared_removal_and_untied_full_both_directions(saved_no_joint_ce, other):
    _, saved = snapshot(other)
    with pytest.raises(ValueError):
        bars(VARIANT).on_load_checkpoint(saved)
    with pytest.raises(ValueError):
        bars(other).on_load_checkpoint(copy.deepcopy(saved_no_joint_ce))


@pytest.mark.parametrize(
    "fault",
    [
        "missing_history",
        "missing_catalog",
        "missing_optimizer",
        "missing_scheduler",
        "moment_shape",
        "duplicate_parameter",
        "wrong_lr",
        "variant",
        "loss_weight",
        "residual_sharing",
        "cold",
    ],
)
def test_restore_rejects_incomplete_or_relabelled_identity(saved_no_joint_ce, fault):
    saved = copy.deepcopy(saved_no_joint_ce)
    optimizer = saved["optimizer_states"][0]
    if fault == "missing_history":
        del saved["state_dict"]["history_collaborative_residual.weight"]
    elif fault == "missing_catalog":
        del saved["state_dict"]["collaborative_residual.weight"]
    elif fault == "missing_optimizer":
        del saved["optimizer_states"]
    elif fault == "missing_scheduler":
        del saved["lr_schedulers"]
    elif fault == "moment_shape":
        identifier = optimizer["param_groups"][1]["params"][1]
        optimizer["state"][identifier]["exp_avg"] = optimizer["state"][identifier]["exp_avg"][:-1]
    elif fault == "duplicate_parameter":
        optimizer["param_groups"][1]["params"][1] = optimizer["param_groups"][1]["params"][0]
    elif fault == "wrong_lr":
        optimizer["param_groups"][1]["lr"] = optimizer["param_groups"][0]["lr"]
    elif fault == "variant":
        saved["copmrec_formal_release"]["variant"] = "untied_residual"
    elif fault == "loss_weight":
        saved["copmrec_unified_scratch"]["loss_weights"]["joint_catalog_ce"] = 1
    elif fault == "residual_sharing":
        saved["copmrec_collaborative_residual"]["sharing"] = "history_and_catalog_after_content_projection"
    else:
        saved["state_dict"]["history_collaborative_residual.weight"][-1, 0] = 1
    with pytest.raises(ValueError):
        bars(VARIANT).on_load_checkpoint(saved)


@pytest.fixture(scope="module")
def bash():
    candidates = [Path(r"D:\development\Git\bin\bash.exe"), Path(r"C:\Program Files\Git\bin\bash.exe")]
    executable = next((path for path in candidates if path.is_file()), None)
    if executable is None:
        pytest.skip("Git Bash is required for launcher tests.")
    return str(executable)


@pytest.mark.parametrize("stage", ["train", "inference"])
@pytest.mark.parametrize("notes_style", ["split", "equals"])
def test_script_composes_structured_untied_removal_identity_and_preserves_overrides(bash, stage, notes_style):
    notes = '独立双残差 "目录 CE=0"'
    args = [
        "--data-dir",
        "data/beauty spaced",
        "--dataset",
        "beauty",
        "--semantic-id-path",
        "sid.pt",
        "--embedding-path",
        "content.pt",
        "--variant",
        VARIANT,
        "--seed",
        "42",
        "--dry-run",
        "--devices",
        "[0,1]" if stage == "train" else "[0]",
    ]
    args += ["--notes", notes] if notes_style == "split" else ["--notes=" + notes]
    if stage == "inference":
        args += ["--checkpoint", "own.ckpt", "--checkpoint-sha256", "8" * 64]
    args.append("model.root.generation_candidates=17")
    command = 'uv() { printf "%s\\n" "$@"; }; export -f uv; bash ' + shlex.join(
        ["bars_ablation_" + stage + ".sh", *args]
    )
    result = subprocess.run([bash], input=command, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    argv = result.stdout.splitlines()
    assert "--dry-run" in argv
    overrides = [value for value in argv[argv.index("src.main") + 1 :] if value != "--dry-run"]
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        cfg = compose(config_name="main", overrides=overrides)
    cfg.paths.output_dir = "logs/test"
    cfg.paths.work_dir = "."
    cfg.paths.profile_dir = "logs/test/profile"
    OmegaConf.resolve(cfg)
    assert cfg.model.root.variant == cfg.formal_release.variant == VARIANT
    assert cfg.training_objective.joint_catalog_ce == 0 and cfg.training_objective.mixture_nll == 1
    assert cfg.training_objective.sid_ce == 1
    assert cfg.alpha_policy == "learned" and cfg.fixed_mixture_alpha is None
    assert cfg.residual_sharing == "untied_history_catalog" and cfg.residual_table_count == 2
    assert cfg.residual_comparison_protocol == "bars-untied-mechanism-beauty42-20261019-v1"
    assert cfg.model.root.generation_candidates == 17 and cfg.logger.wandb.notes == notes
    writer = cfg.callbacks.wandb_checkpoint_writer if stage == "train" else cfg.callbacks.wandb_artifact_writer
    assert writer.metadata.ablation_variant == VARIANT
    assert writer.metadata.residual_sharing == "untied_history_catalog" and writer.metadata.residual_table_count == 2
    assert writer.metadata.alpha_policy == "learned" and writer.metadata.fixed_mixture_alpha is None
    assert cfg.model.root.evaluation_mode == "dense"
    assert cfg.model.root.prediction_mode == ("dense" if stage == "train" else "hybrid")


@pytest.mark.parametrize("variant", ["", "untied_no_joint_ce_typo"])
def test_new_variant_whitelist_rejects_empty_or_unknown_input(bash, variant):
    command = "source bars_m3_common.sh; bars_m3_parse " + shlex.quote("--variant=" + variant)
    command += "; bars_m3_require_variant"
    result = subprocess.run([bash], input=command, cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 2
