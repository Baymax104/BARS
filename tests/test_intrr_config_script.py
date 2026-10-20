"""IntRR 仅改变模型和商品表示；配置与真实脚本锁定 TIGER 通用协议。"""

import shlex
import subprocess
from pathlib import Path

import pytest
from bash_fixture import bash as bash_fixture
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

import src.utils.hydra_resolvers  # noqa: F401
from src.utils.launcher import apply_dry_run_overrides

bash = bash_fixture
ROOT = Path(__file__).resolve().parents[1]
SID = "wandb://baymaxam/GRID/sid?role=semantic_id&file=x=y.pt"
CHECKPOINT = "checkpoints with spaces/best_step=004200.ckpt"


def compose_baseline(method, mode, extra=()):
    overrides = [
        f"experiment={method}_{mode}",
        'data_dir="data/test dataset"',
        f'semantic_id_path="{SID}"',
        "devices=[0,1]",
        "seed=200",
    ]
    overrides += ["group=rkmeans"] if method == "tiger" else ["sid_type=rkmeans"]
    if mode == "inference":
        overrides += [f'ckpt_path="{CHECKPOINT}"']
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        return compose(config_name="main", overrides=[*overrides, *extra])


def plain(value):
    # 保留相同插值表达式，避免解析仅运行时存在的 hydra:runtime.output_dir。
    return OmegaConf.to_container(value, resolve=False)


@pytest.mark.parametrize("mode", ["train", "inference"])
def test_composed_nonmodel_protocol_is_identical_to_tiger(mode):
    tiger, intrr = (compose_baseline(method, mode) for method in ("tiger", "intrr"))
    for field in ("trainer", "callbacks", "logger", "paths", "extras"):
        assert plain(intrr[field]) == plain(tiger[field]), field
    for field in (
        "data_dir",
        "semantic_id_path",
        "sequence_length",
        "num_hierarchies",
        "codebook_size",
        "devices",
        "seed",
    ):
        assert intrr[field] == tiger[field], field
    assert intrr.sequence_length == 180 and intrr.num_hierarchies == 4 and intrr.codebook_size == 256
    assert intrr.group == "intrr" and intrr.sid_type == "rkmeans"
    assert intrr.upstream_commit == "806e0f1969ed61a0748902649b335c0ea066de00"
    assert intrr.model.root.top_k_for_generation == 10 and intrr.model.root.should_check_prefix
    assert intrr.model.root.sequence_length == tiger.sequence_length
    assert not intrr.dry_run

    tiger_data, intrr_data = plain(tiger.data), plain(intrr.data)
    catalog = intrr_data.pop("catalog")
    assert catalog["_target_"] == "src.data.components.intrr.load_intrr_catalog"
    assert intrr_data["collate"].pop("catalog") == "${data.catalog}"
    assert intrr_data["collate"].pop("sequence_length") == "${sequence_length}"
    assert intrr_data["collate"]["_target_"] == "src.data.components.intrr.intrr_collate"
    intrr_data["collate"]["_target_"] = tiger_data["collate"]["_target_"]
    assert intrr_data == tiger_data

    if mode == "train":
        assert intrr.validation_implementation == "history-encoding-reuse-v1"
        assert plain(intrr.model.training_model_config) == plain(tiger.model.training_model_config)
        assert plain(intrr.model.metrics) == plain(tiger.model.metrics)
        assert intrr.model.training_model_config.optimizer._target_ == "torch.optim.Adam"
        assert intrr.model.training_model_config.optimizer.lr == 0.0005
        assert intrr.model.training_model_config.optimizer.weight_decay == 0.000001
        assert intrr.model.training_model_config.scheduler is None
        assert intrr.trainer.root.max_steps == 50000 and intrr.trainer.root.val_check_interval == 100
        assert intrr.trainer.root.accumulate_grad_batches == 1 and intrr.trainer.root.precision == "32-true"
        assert intrr.trainer.root.strategy == "ddp"
        assert intrr.data.train_dataloader.batch_size_per_device == 128
        assert intrr.data.val_dataloader.batch_size_per_device == 64
        assert intrr.callbacks.model_checkpoint.monitor == "val/ndcg@10"
        assert intrr.callbacks.model_checkpoint.mode == "max"
        assert intrr.run_test_after_training is False
    else:
        assert intrr.ckpt_path == CHECKPOINT
        assert intrr.data.predict_dataloader.batch_size_per_device == 32
        assert intrr.callbacks.tiger_prediction_metrics.top_ks == [5, 10]


def base_arguments(mode):
    args = [
        f"intrr_{mode}.sh",
        "--data-dir",
        "data/test dataset",
        "--semantic-id-path",
        SID,
        "--group",
        "rkmeans",
        "--notes",
        "IntRR protocol check",
    ]
    if mode == "inference":
        args += ["--ckpt-path", CHECKPOINT]
    return args


def invoke(bash, args, environment=""):
    script = "\n".join(
        [
            'uv() { printf "%s\\n" "$@"; }',
            "export -f uv",
            "unset NPROC_PER_NODE MASTER_PORT DEVICES",
            environment,
            "bash " + shlex.join(args),
        ]
    )
    return subprocess.run([bash], input=script, cwd=ROOT, text=True, capture_output=True)


def compose_script_output(output):
    lines = output.stdout.splitlines()
    overrides = [value for value in lines[6:] if value != "--dry-run"]
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        return compose(config_name="main", overrides=overrides)


@pytest.mark.parametrize("mode", ["train", "inference"])
@pytest.mark.parametrize("equals", [False, True])
def test_real_scripts_quote_notes_paths_and_keep_trailing_override_priority(bash, mode, equals):
    note = 'literal $(printf unexpected) "quoted" \\ text ; = &'
    notes = ["--notes=" + note] if equals else ["--notes", note]
    result = invoke(
        bash,
        [*base_arguments(mode), *notes, "--wandb-group", "paper_main_intrr_beauty", "--dry-run", "seed=2026"],
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[:2] == ["run", "torchrun"]
    assert lines[2] == f"--nproc_per_node={2 if mode == 'train' else 1}"
    assert lines[4:6] == ["-m", "src.main"]
    assert "--dry-run" in lines and lines[-1] == "seed=2026"
    cfg = compose_script_output(result)
    assert cfg.seed == 2026 and cfg.logger.wandb.notes == note
    assert cfg.data_dir == "data/test dataset" and cfg.semantic_id_path == SID
    assert cfg.group == "paper_main_intrr_beauty" and cfg.logger.wandb.group == cfg.group
    assert cfg.sid_type == "rkmeans"
    if mode == "inference":
        assert cfg.ckpt_path == CHECKPOINT


@pytest.mark.parametrize("mode", ["train", "inference"])
def test_scripts_default_to_formal_run_and_match_tiger_device_defaults(bash, mode):
    result = invoke(bash, base_arguments(mode))
    assert result.returncode == 0, result.stderr
    assert "--dry-run" not in result.stdout.splitlines()
    cfg = compose_script_output(result)
    assert not cfg.dry_run
    assert cfg.devices == ([0, 1] if mode == "train" else [0])


@pytest.mark.parametrize("equals", [False, True])
def test_master_port_cli_has_priority_over_environment_and_override_is_last(bash, equals):
    option = ["--master-port=29548"] if equals else ["--master-port", "29548"]
    result = invoke(
        bash,
        [*base_arguments("train"), *option, "--devices", "[2,3]", "trainer.root.max_steps=5"],
        "export NPROC_PER_NODE=2\nexport MASTER_PORT=29547",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[:6] == [
        "run",
        "torchrun",
        "--nproc_per_node=2",
        "--master_port=29548",
        "-m",
        "src.main",
    ]
    assert result.stdout.splitlines()[-1] == "trainer.root.max_steps=5"
    cfg = compose_script_output(result)
    assert cfg.devices == [2, 3] and cfg.trainer.root.max_steps == 5


def test_environment_port_and_process_override(bash):
    result = invoke(
        bash,
        base_arguments("inference"),
        "export NPROC_PER_NODE=2\nexport MASTER_PORT=29549\nexport DEVICES='[0,1]'",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[:6] == [
        "run",
        "torchrun",
        "--nproc_per_node=2",
        "--master_port=29549",
        "-m",
        "src.main",
    ]


def test_checkpoint_alias_is_hydra_quoted(bash):
    args = base_arguments("inference")
    args[args.index("--ckpt-path")] = "--checkpoint"
    result = invoke(bash, args)
    assert result.returncode == 0, result.stderr
    assert compose_script_output(result).ckpt_path == CHECKPOINT


@pytest.mark.parametrize(
    ("note", "data_dir"),
    [
        ("trailing slash \\", r"C:\research\GRID\data"),
        ('slash before \\"quote"', r"C:\research\GRID\data\beauty"),
        (r"two slashes \\ then \\\\ four", "\\\\server\\research\\beauty\\"),
        ('apostrophe \' and "quotes" \\\\', "C:\\project with spaces\\beauty\\"),
    ],
)
def test_backslash_runs_and_windows_paths_survive_actual_hydra_compose(bash, note, data_dir):
    result = invoke(bash, [*base_arguments("train"), "--notes", note, "--data-dir", data_dir])
    assert result.returncode == 0, result.stderr
    cfg = compose_script_output(result)
    assert cfg.logger.wandb.notes == note
    assert cfg.data_dir == data_dir


@pytest.mark.parametrize(
    "extra",
    [
        ["--data-dir="],
        ["--semantic-id-path="],
        ["--notes="],
        ["--notes", ""],
        ["--notes"],
        ["--group=unknown"],
        ["--seed=-1"],
        ["--seed=wrong"],
        ["--master-port=0"],
        ["--master-port=65536"],
        ["--unknown"],
    ],
)
def test_invalid_cli_arguments_fail_before_launch(bash, extra):
    result = invoke(bash, [*base_arguments("train"), *extra])
    assert result.returncode == 2
    assert not result.stdout


@pytest.mark.parametrize("option", ["--data-dir", "--semantic-id-path", "--notes", "--group", "--ckpt-path"])
def test_missing_required_options_fail_before_launch(bash, option):
    mode = "inference" if option == "--ckpt-path" else "train"
    args = base_arguments(mode)
    index = args.index(option)
    del args[index : index + 2]
    assert invoke(bash, args).returncode == 2


@pytest.mark.parametrize(
    "environment", ["export NPROC_PER_NODE=0", "export NPROC_PER_NODE=bad", "export MASTER_PORT=0"]
)
def test_invalid_environment_fails_before_launch(bash, environment):
    assert invoke(bash, base_arguments("train"), environment).returncode == 2


@pytest.mark.parametrize("mode", ["train", "inference"])
def test_dry_run_uses_shared_no_publish_overrides(mode):
    cfg = compose_baseline("intrr", mode)
    cfg.dry_run = True
    apply_dry_run_overrides(cfg)
    assert cfg.logger.wandb is None
    if mode == "train":
        assert cfg.trainer.root.max_steps == 1 and cfg.trainer.root.limit_val_batches == 0
        assert cfg.callbacks.model_checkpoint is None and cfg.callbacks.wandb_checkpoint_writer is None
        assert not cfg.run_test_after_training
    else:
        assert cfg.trainer.root.limit_predict_batches == 1 and cfg.callbacks.wandb_artifact_writer is None


def test_script_shell_syntax(bash):
    for path in ("intrr_common.sh", "intrr_train.sh", "intrr_inference.sh"):
        result = subprocess.run([bash, "-n", path], cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
