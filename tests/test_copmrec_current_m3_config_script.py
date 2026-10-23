"""当前 M3 根脚本参数、Hydra 选点协议与发布身份。"""

import subprocess

import pytest
from bash_fixture import bash as bash_fixture
from omegaconf import OmegaConf
from test_copmrec_v2_config_script import compose_argv, launch

from src.recommendation.copmrec.ablation import CURRENT_M3_PROTOCOL, CURRENT_M3_VARIANTS

bash = bash_fixture


@pytest.mark.parametrize("variant", CURRENT_M3_VARIANTS)
@pytest.mark.parametrize("stage", ["train", "inference"])
@pytest.mark.parametrize("equals,dry_run", [(True, False), (False, True)])
def test_current_controls_compose_matching_recipe_and_preserve_user_overrides(bash, variant, stage, equals, dry_run):
    notes = '当前消融 "alpha=0.5", 空格与中文'
    args = ["--variant=" + variant] if equals else ["--variant", variant]
    args += ["--notes=" + notes] if equals else ["--notes", notes]
    args += ["--devices", "[0,1]" if stage == "train" else "[0]"]
    if dry_run:
        args.append("--dry-run")
    if stage == "inference":
        args += ["--checkpoint", "own current best.ckpt", "--checkpoint-sha256", "8" * 64]
    args += ["model.root.generation_candidates=17"]
    result = launch(bash, "copmrec_ablation_" + stage + ".sh", args)
    assert result.returncode == 0, result.stderr
    argv = result.stdout.splitlines()
    cfg = compose_argv(argv)
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert ("--dry-run" in argv) is dry_run
    assert cfg.model.root.variant == cfg.formal_release.variant == variant
    assert cfg.m3_protocol == cfg.formal_release.m3_protocol == CURRENT_M3_PROTOCOL
    assert cfg.model.root.validation_selection_mode == cfg.model.root.evaluation_mode == "hybrid"
    assert cfg.model.root.prediction_mode == "hybrid"
    assert cfg.alpha_policy == "frozen_0.5" and cfg.fixed_mixture_alpha == 0.5
    assert cfg.training_objective.sid_ce == 1 and cfg.training_objective.mixture_nll == 0
    assert cfg.training_objective.joint_catalog_ce == int("no_joint_ce" not in variant)
    assert cfg.group == cfg.logger.wandb.group == "ablation_main"
    assert cfg.logger.wandb.notes == notes and cfg.model.root.generation_candidates == 17
    assert "fixed_alpha_0.5" in cfg.run_display_name
    assert cfg.residual_comparison_protocol == CURRENT_M3_PROTOCOL
    assert cfg.residual_table_count == (2 if variant.startswith("untied_") else 1)
    writer = cfg.callbacks.wandb_checkpoint_writer if stage == "train" else cfg.callbacks.wandb_artifact_writer
    assert writer.metadata.ablation_variant == variant
    assert writer.metadata.m3_protocol == CURRENT_M3_PROTOCOL
    assert writer.metadata.alpha_policy == "frozen_0.5"
    if stage == "train":
        assert cfg.ckpt_path is None and cfg.trainer.root.max_steps == 50000
        assert cfg.trainer.root.val_check_interval == 500
        assert cfg.data.train_dataloader.batch_size_per_device == 128
        assert cfg.trainer.root.strategy.find_unused_parameters is False
        assert cfg.callbacks.model_checkpoint.monitor == "val/ndcg@10"
    else:
        assert writer.metadata.deployment_contract.alpha_source == "fixed"
        assert writer.metadata.deployment_contract.fixed_mixture_alpha == 0.5


@pytest.mark.parametrize("variant", CURRENT_M3_VARIANTS)
@pytest.mark.parametrize("invalid", [["--notes="], ["--notes", ""], ["--group="], [""]])
def test_current_control_rejects_empty_values_before_execution(bash, variant, invalid):
    result = launch(bash, "copmrec_ablation_train.sh", ["--variant=" + variant, *invalid])
    assert result.returncode == 2 and "src.main" not in result.stdout


def test_current_control_whitelist_and_shell_syntax(bash):
    result = launch(bash, "copmrec_ablation_train.sh", ["--variant=untied_fixed_alpha_half_no_joint_ce_typo"])
    assert result.returncode == 2 and "src.main" not in result.stdout
    for script in ("copmrec_m3_common.sh", "copmrec_ablation_train.sh", "copmrec_ablation_inference.sh"):
        result = subprocess.run([bash, "-n", script], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
