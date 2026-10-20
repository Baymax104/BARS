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
    assert cfg.m3_protocol == "bars-untied-mechanism-beauty42-20261019-v1"
    assert "--dry-run" in result.stdout.splitlines()
    assert cfg.callbacks.structured_analysis.output_dir == "logs/test/analysis"
    if analysis == "contributions":
        assert cfg.model.root._target_.endswith("CoPMRecContributionDiagnosis")
        assert cfg.trainer.root.accelerator == "cpu"
        assert cfg.ckpt_path is None
        assert set(cfg.prediction_paths) == set(cfg.prediction_sha256s) == {"untied", "shared", "no_residual"}
        assert cfg.model.root.prediction_bundles.expected_deployment_contract.history_exclusion is False
    else:
        assert cfg.model.root._target_.endswith("CoPMRecMechanismDiagnosis")
        assert cfg.model.root.backbone.variant == "untied_residual"
        assert cfg.model.root.backbone.prediction_mode == "hybrid"
        assert cfg.model.root.backbone.training_model_config is None
        assert cfg.model.root.checkpoint.sha256 == SHA
        assert cfg.model.root.checkpoint.reference == "own best.ckpt"
        assert cfg.model.root.reference_predictions.sha256 == cfg.prediction_sha256s.untied
        assert cfg.trainer.root.accelerator == "gpu"


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
        (["--analysis=generation"], ""),
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
