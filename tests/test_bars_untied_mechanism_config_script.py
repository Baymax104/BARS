"""机制入口的真实shell参数解析与轻量Hydra装配，不运行experiment。"""

import subprocess

import pytest
from bash_fixture import bash as bash_fixture
from formal_config_helpers import ROOT, compose_argv
from test_copmrec_v2_config_script import BASE, launch

bash = bash_fixture
SCRIPT = "bars_untied_mechanism.sh"
SHA = "c" * 64


@pytest.mark.parametrize("analysis", ["contributions", "generation"])
@pytest.mark.parametrize("notes", [["--notes", "中文 notes with spaces"], ["--notes=中文 notes with spaces"]])
def test_mechanism_script_composes_correct_component_and_overrides(bash, analysis, notes):
    identity = [] if analysis == "contributions" else ["--checkpoint", "own best.ckpt", "--checkpoint-sha256", SHA]
    result = launch(
        bash,
        SCRIPT,
        [
            *BASE,
            "--devices",
            "1",
            "--analysis",
            analysis,
            *identity,
            *notes,
            "--dry-run",
            "model.root.bootstrap_repetitions=3",
        ],
    )
    assert result.returncode == 0, result.stderr
    cfg = compose_argv(result.stdout.splitlines())
    assert cfg.run_mode == "analysis"
    assert cfg.model.root.bootstrap_repetitions == 3
    assert cfg.model.root.num_hierarchies == 4
    assert cfg.logger.wandb.notes == "中文 notes with spaces"
    assert cfg.m3_protocol == "bars-fixed-half-hybrid-m3-20261023-v1"
    assert "--dry-run" in result.stdout.splitlines()
    assert cfg.callbacks.structured_analysis.output_dir == "logs/test/analysis"
    if analysis == "contributions":
        assert cfg.model.root._target_.endswith("CoPMRecContributionDiagnosis")
        assert cfg.trainer.root.accelerator == "cpu"
        assert cfg.ckpt_path is None
        assert set(cfg.prediction_paths) == set(cfg.prediction_sha256s) == {"untied"}
        assert "prt5r0v5" in cfg.prediction_paths.untied
        assert cfg.model.root.prediction_bundles.minimum_conditions == 2
        assert cfg.model.root.prediction_bundles.expected_source_variants.untied == "untied_fixed_alpha_half_no_mixture"
        assert cfg.model.root.prediction_bundles.expected_source_variants.shared == "shared_fixed_alpha_half_no_mixture"
        assert cfg.model.root.prediction_bundles.expected_deployment_contract.history_exclusion is False
    else:
        assert cfg.model.root._target_.endswith("CoPMRecMechanismDiagnosis")
        assert cfg.model.root.backbone.variant == "untied_fixed_alpha_half_no_mixture"
        assert cfg.model.root.backbone.validation_selection_mode == "hybrid"
        assert cfg.model.root.backbone.evaluation_mode == "hybrid"
        assert cfg.model.root.backbone.prediction_mode == "hybrid"
        assert cfg.model.root.backbone.training_model_config is None
        assert cfg.model.root.checkpoint.sha256 == SHA
        assert cfg.model.root.checkpoint.reference == "own best.ckpt"
        assert cfg.model.root.reference_predictions.sha256 == cfg.prediction_sha256s.untied
        assert cfg.trainer.root.accelerator == "gpu"
    contract = cfg.model.expected_deployment_contract
    assert contract.alpha_policy == "frozen_0.5" and contract.alpha_source == "fixed"
    assert contract.fixed_mixture_alpha == 0.5


def test_mechanism_not_dry_by_default_and_extra_override_wins(bash):
    result = launch(bash, SCRIPT, [*BASE, "--devices", "1", "--analysis=contributions", "trainer.root.accelerator=cpu"])
    assert result.returncode == 0, result.stderr
    assert "--dry-run" not in result.stdout.splitlines()
    assert compose_argv(result.stdout.splitlines()).trainer.root.accelerator == "cpu"


def test_cpu_contributions_and_gpu_mechanism_keep_correct_devices(bash):
    cpu = launch(bash, SCRIPT, [*BASE, "--devices", "[0]", "--analysis=contributions"])
    assert cpu.returncode == 0, cpu.stderr
    assert compose_argv(cpu.stdout.splitlines()).trainer.root.devices == 1
    gpu = launch(
        bash,
        SCRIPT,
        [*BASE, "--devices", "[3]", "--analysis=generation", "--checkpoint=own.ckpt", "--checkpoint-sha256=" + SHA],
    )
    assert gpu.returncode == 0, gpu.stderr
    assert list(compose_argv(gpu.stdout.splitlines()).trainer.root.devices) == [3]


def test_analysis_dry_run_disables_epoch_writer_and_limits_batches(bash):
    from src.utils.launcher import apply_dry_run_overrides

    result = launch(bash, SCRIPT, [*BASE, "--devices", "1", "--analysis=contributions", "--dry-run"])
    assert result.returncode == 0, result.stderr
    cfg = compose_argv(result.stdout.splitlines())
    cfg.dry_run = True
    apply_dry_run_overrides(cfg)
    assert cfg.trainer.root.limit_test_batches == 1
    assert cfg.callbacks.structured_analysis is None
    assert cfg.callbacks.wandb_artifact_lineage is None
    assert cfg.logger.wandb is None


@pytest.mark.parametrize(
    "args,prefix",
    [
        (["--analysis", ""], ""),
        (["--analysis="], ""),
        (["--analysis=invalid"], ""),
        (["--analysis=contributions", "--checkpoint=old.ckpt"], ""),
        (["--analysis=contributions", "--variant=untied_residual"], ""),
        (["--analysis=contributions", "--checkpoint-sha256=" + SHA], ""),
        (["--analysis=generation", "--checkpoint=own.ckpt"], ""),
        (["--analysis=generation", "--checkpoint-sha256=bad", "--checkpoint=own.ckpt"], ""),
        (["--analysis=generation", "--checkpoint-sha256=" + SHA], ""),
        (["--analysis=contributions", "--notes="], ""),
        (["--analysis=contributions", "--notes", ""], ""),
        (["--analysis=contributions", ""], ""),
        (["--analysis=contributions"], "export NPROC_PER_NODE=2; "),
    ],
)
def test_invalid_analysis_arguments_rejected_before_execution(bash, args, prefix):
    result = launch(bash, SCRIPT, [*BASE, "--devices", "1", *args], prefix)
    assert result.returncode != 0
    assert "src.main" not in result.stdout


def test_mechanism_shell_syntax(bash):
    result = subprocess.run([bash, "-n", SCRIPT], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_generation_defaults_to_audited_current_full(bash):
    result = launch(bash, SCRIPT, [*BASE, "--devices", "1", "--analysis=generation"])
    assert result.returncode == 0, result.stderr
    cfg = compose_argv(result.stdout.splitlines())
    assert "httwyhka" in cfg.model.root.checkpoint.reference
    assert cfg.model.root.checkpoint.sha256 == "f2ffd7939483c4e16fa9359a2a856865386d0823d6285321c53df1f1391ca4c9"
    assert "prt5r0v5" in cfg.model.root.reference_predictions.file_path
    assert cfg.model.root.reference_predictions.sha256 == "7bd54d23e33b6b89b4d7de568f030172819293417fd5f74a4fc39a5ca1097065"


def test_explicit_legacy_source_composes_original_selection_and_alpha(bash):
    result = launch(
        bash, SCRIPT,
        [
            *BASE, "--devices", "1", "--analysis=generation", "--checkpoint=old.ckpt",
            "--checkpoint-sha256=" + SHA, "analysis_source_variant=untied_residual",
            'prediction_paths.untied="frozen old.pt"', 'prediction_sha256s.untied="' + SHA + '"',
        ],
    )
    assert result.returncode == 0, result.stderr
    cfg = compose_argv(result.stdout.splitlines())
    assert cfg.m3_protocol == "bars-untied-mechanism-beauty42-20261019-v1"
    assert cfg.model.root.backbone.variant == "untied_residual"
    assert cfg.model.root.backbone.validation_selection_mode == cfg.model.root.backbone.evaluation_mode == "dense"
    assert cfg.model.expected_deployment_contract.alpha_policy == "learned"
    assert cfg.model.expected_deployment_contract.alpha_source == "checkpoint"
    assert cfg.model.expected_deployment_contract.fixed_mixture_alpha is None
    assert cfg.model.root.reference_predictions.file_path == "frozen old.pt"
    assert "来源=untied_residual" in cfg.logger.wandb.notes
    assert "alpha=learned/None" in cfg.logger.wandb.notes


def test_new_comparison_sources_are_explicit_extra_overrides(bash):
    result = launch(
        bash, SCRIPT,
        [
            *BASE, "--devices", "1", "--analysis=contributions",
            '+prediction_paths.shared="new matched shared.pt"', '+prediction_sha256s.shared="' + SHA + '"',
        ],
    )
    assert result.returncode == 0, result.stderr
    cfg = compose_argv(result.stdout.splitlines())
    assert set(cfg.prediction_paths) == set(cfg.prediction_sha256s) == {"untied", "shared"}
    assert cfg.prediction_paths.shared == "new matched shared.pt"
