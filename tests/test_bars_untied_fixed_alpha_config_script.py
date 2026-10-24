"""临时双残差固定 alpha 的脚本参数与 Hydra 组件身份。"""

import pytest
from bash_fixture import bash as bash_fixture
from omegaconf import OmegaConf
from test_bars_v2_config_script import compose_argv, launch

bash = bash_fixture


@pytest.mark.parametrize("stage", ["train", "inference"])
@pytest.mark.parametrize("equals", [False, True])
@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("suffix,alpha,policy", [("one", 1.0, "frozen_1"), ("half", 0.5, "frozen_0.5")])
def test_temporary_untied_fixed_alpha_composes_exact_endpoint_and_custom_identity(
    bash, stage, equals, dry_run, suffix, alpha, policy
):
    variant = "untied_fixed_alpha_" + suffix
    notes = f'temporary "alpha={alpha}", keep in W&B only'
    args = ["--variant=" + variant] if equals else ["--variant", variant]
    args += ["--devices", "[0,1]" if stage == "train" else "[0]"]
    args += ["--notes=" + notes] if equals else ["--notes", notes]
    group = f"temporary_bars_alpha_{suffix}_beauty_seed42"
    args += ["--group", group]
    if dry_run:
        args += ["--dry-run"]
    task_name = f"bars_temp_beauty_seed42_{variant}_train"
    args += ["task_name=" + task_name]
    display = f"temporary alpha={alpha} custom display"
    args += [f'logger.wandb.name="{display}"', "model.root.generation_candidates=17"]
    if stage == "inference":
        args += ["--checkpoint", "own temporary.ckpt", "--checkpoint-sha256", "8" * 64]
    result = launch(bash, f"bars_ablation_{stage}.sh", args)
    assert result.returncode == 0, result.stderr
    cfg = compose_argv(result.stdout.splitlines())
    OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)
    assert ("--dry-run" in result.stdout.splitlines()) is dry_run
    assert cfg.model.root.variant == cfg.formal_release.variant == variant
    assert cfg.alpha_policy == policy and cfg.fixed_mixture_alpha == alpha
    assert cfg.model.ablation_alpha[variant].source == "fixed"
    assert cfg.model.root.content_mixture_alpha == 0.5
    assert cfg.residual_sharing == "untied_history_catalog" and cfg.residual_table_count == 2
    assert cfg.residual_comparison_protocol == f"temporary-bars-untied-alpha-{suffix}-v1"
    assert (
        cfg.training_objective.sid_ce
        == cfg.training_objective.joint_catalog_ce
        == cfg.training_objective.mixture_nll
        == 1.0
    )
    assert cfg.group == cfg.logger.wandb.group == group
    assert cfg.logger.wandb.name == display
    assert cfg.logger.wandb.notes == notes and cfg.model.root.generation_candidates == 17
    writer = cfg.callbacks.wandb_checkpoint_writer if stage == "train" else cfg.callbacks.wandb_artifact_writer
    assert writer.task_name == cfg.task_name == task_name
    assert writer.artifact_name.startswith(cfg.task_name + "-")
    assert writer.metadata.ablation_variant == variant
    assert writer.metadata.alpha_policy == policy and writer.metadata.fixed_mixture_alpha == alpha
    assert writer.metadata.residual_sharing == "untied_history_catalog" and writer.metadata.residual_table_count == 2
    if stage == "train":
        assert cfg.ckpt_path is None and cfg.trainer.root.max_steps == 50000
        assert cfg.trainer.root.val_check_interval == 500 and cfg.trainer.root.precision == "32-true"
        assert cfg.data.train_dataloader.batch_size_per_device == 128
        assert "--nproc_per_node=2" in result.stdout.splitlines()


@pytest.mark.parametrize("invalid", [["--notes="], ["--notes", ""], ["--group="], [""]])
def test_half_rejects_empty_values_before_launch(bash, invalid):
    result = launch(bash, "bars_ablation_train.sh", ["--variant=untied_fixed_alpha_half", *invalid])
    assert result.returncode == 2 and "src.main" not in result.stdout
