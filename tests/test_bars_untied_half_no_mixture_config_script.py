"""检查固定半半去混合损失的真实脚本和 Hydra 装配。"""

import pytest
from bash_fixture import bash as bash_fixture
from omegaconf import OmegaConf
from test_bars_v2_config_script import compose_argv, launch

bash = bash_fixture
VARIANT = "untied_fixed_alpha_half_no_mixture"


@pytest.mark.parametrize("stage", ["train", "inference"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_two_loss_variant_composes_and_preserves_script_overrides(bash, stage, dry_run):
    notes = 'temporary "alpha=0.5", no mixture loss; W&B only'
    args = ["--variant=" + VARIANT, "--notes", notes, "--devices", "[0,1]" if stage == "train" else "[0]"]
    if dry_run:
        args.append("--dry-run")
    if stage == "inference":
        args += ["--checkpoint", "own half no mixture.ckpt", "--checkpoint-sha256", "8" * 64]
    args += ["model.root.generation_candidates=17"]
    result = launch(bash, "bars_ablation_" + stage + ".sh", args)
    assert result.returncode == 0, result.stderr
    argv = result.stdout.splitlines()
    cfg = compose_argv(argv)
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert ("--dry-run" in argv) is dry_run
    assert cfg.ablation_variant == cfg.model.root.variant == VARIANT
    assert cfg.alpha_policy == "frozen_0.5" and cfg.fixed_mixture_alpha == 0.5
    assert cfg.residual_sharing == "untied_history_catalog" and cfg.residual_table_count == 2
    assert cfg.training_objective.sid_ce == cfg.training_objective.joint_catalog_ce == 1.0
    assert cfg.training_objective.mixture_nll == 0.0
    assert cfg.logger.wandb.group == cfg.group == "bars_main"
    assert cfg.logger.wandb.notes == notes and cfg.model.root.generation_candidates == 17
    assert "untied_fixed_alpha_0.5_no_mixture" in cfg.run_display_name
    assert cfg.model.root.validation_selection_mode == cfg.model.root.evaluation_mode == "hybrid"
    assert cfg.model.root.prediction_mode == "hybrid"
    if stage == "train":
        assert cfg.ckpt_path is None and cfg.trainer.root.max_steps == 50000
        assert cfg.trainer.root.val_check_interval == 500
        assert cfg.data.train_dataloader.batch_size_per_device == 128
        assert cfg.callbacks.model_checkpoint.monitor == "val/ndcg@10"
        assert cfg.callbacks.wandb_checkpoint_writer.metadata.validation_selection_mode == "hybrid"
