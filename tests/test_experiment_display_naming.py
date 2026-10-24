"""显示分组跨数据集/seed 稳定，内部产物身份继续独立。"""

import re
import shlex
import subprocess

import pytest
from bash_fixture import bash as bash_fixture
from formal_config_helpers import ROOT
from hydra import compose, initialize_config_dir

from src.utils.hydra_resolvers import dataset_slug

bash = bash_fixture


def config(experiment, *overrides):
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        return compose(
            config_name="main",
            overrides=[
                f"experiment={experiment}",
                "++dataset_name=beauty",
                "++data_dir=data/beauty",
                "++devices=[0,1]",
                "++semantic_id_path=semantic.pt",
                "++embedding_path=embedding.pt",
                "++sid_type=rkmeans",
                *overrides,
            ],
        )


@pytest.mark.parametrize("dataset,seed", [("beauty", 42), ("sports", 200), ("toys", 2026)])
@pytest.mark.parametrize(
    "experiment,group,stage",
    [
        ("sasrec_train", "sasrec_main", "train"),
        ("sasrec_inference", "sasrec_main", "test"),
        ("liger_train", "liger_main", "train"),
        ("liger_inference", "liger_main", "hybrid_test"),
        ("intrr_train", "intrr_main", "train"),
        ("intrr_inference", "intrr_main", "test"),
        ("tiger_train", "tiger_main", "train"),
        ("tiger_inference", "tiger_main", "test"),
        ("letter_cf_train", "letter_main", "cf_train"),
        ("letter_cf_export", "letter_main", "cf_export"),
        ("letter_tokenizer_train", "letter_main", "tokenizer_train"),
        ("letter_sid", "letter_main", "sid_export"),
        ("letter_train", "letter_main", "train"),
        ("letter_inference", "letter_main", "test"),
        ("sem_embeds_inference", "sem_embeds_main", "semantic_embedding_export"),
        ("rkmeans_train", "rkmeans_main", "quantizer_train"),
        ("rqvae_inference", "rqvae_main", "sid_export"),
        ("rvq_train", "rvq_main", "quantizer_train"),
    ],
)
def test_method_group_and_stage_across_datasets_and_seeds(experiment, group, stage, dataset, seed):
    cfg = config(experiment, f"dataset_name={dataset}", f"seed={seed}")
    assert cfg.group == cfg.logger.wandb.group == group
    assert f"_{dataset}_seed{seed}_" in cfg.run_display_name
    assert cfg.run_display_name.endswith("_" + stage)
    assert re.fullmatch(re.escape(cfg.run_display_name) + r"/\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", cfg.logger.wandb.name)


@pytest.mark.parametrize(
    "variant,group,label",
    [
        (None, "ablation_main", "shared"),
        ("untied_residual", "history", "untied_learned_alpha_mixture"),
        ("no_residual", "ablation_main", "shared_no_residual"),
        ("untied_no_joint_ce", "ablation_main", "untied_no_joint_ce"),
        ("fixed_alpha_one", "ablation_main", "shared_alpha_exploration_fixed_1"),
        ("untied_fixed_alpha_one", "ablation_main", "untied_alpha_exploration_fixed_1"),
        ("untied_fixed_alpha_half", "ablation_main", "untied_alpha_exploration_fixed_0.5"),
        ("untied_fixed_alpha_half_no_mixture", "bars_main", "untied_fixed_alpha_0.5_no_mixture"),
        ("untied_alpha_near_zero", "ablation_main", "untied_alpha_exploration_init_0.0001_learned"),
    ],
)
@pytest.mark.parametrize("stage", ["train", "inference"])
def test_bars_display_classification_preserves_task_and_contract(variant, group, label, stage):
    experiment = "bars_" + ("ablation_" if variant else "") + stage
    cfg = config(experiment, *([f"ablation_variant={variant}"] if variant else []))
    suffix = "train" if stage == "train" else "test"
    assert cfg.group == cfg.logger.wandb.group == group
    assert cfg.run_display_name == f"bars_v2_beauty_seed42_{label}_{suffix}"
    assert cfg.task_name.startswith("bars_v2_beauty_seed42_")
    assert cfg.method == "bars" and cfg.formal_release.protocol == "copmrec-formal-joint-only-v2-v1"
    writer = cfg.callbacks.wandb_checkpoint_writer if stage == "train" else cfg.callbacks.wandb_artifact_writer
    assert writer.task_name == cfg.task_name
    assert writer.artifact_name.startswith(cfg.task_name + "-")


def test_bars_validation_display_and_mechanism_override_remain_independent():
    cfg = config(
        "bars_ablation_inference", "ablation_variant=untied_no_joint_ce",
        "group=mechanism_main", "evaluation_split=validation",
    )
    assert cfg.logger.wandb.group == "mechanism_main"
    assert cfg.run_display_name == "bars_v2_beauty_seed42_untied_no_joint_ce_validation"
    assert cfg.task_name.endswith("_hybrid_inference")
    assert cfg.evidence_phase == "ablation"


@pytest.mark.parametrize("experiment", ["bars_untied_contributions", "bars_untied_mechanism", "bars_diagnosis"])
def test_mechanism_display_defaults(experiment):
    extra = ["diagnosis_analysis=hits"] if experiment == "bars_diagnosis" else []
    cfg = config(experiment, *extra)
    assert cfg.group == cfg.logger.wandb.group == "mechanism_main"
    assert cfg.run_display_name.endswith("_analysis")


@pytest.mark.parametrize("path", ["data/beauty/", "data\\beauty\\", "E:\\datasets\\beauty", "/data/beauty"])
def test_dataset_display_slug_accepts_both_platform_paths(path):
    assert dataset_slug(path) == "beauty"


@pytest.mark.parametrize("equals", [False, True])
def test_tiger_quantizer_and_quoted_group_override_are_separate(bash, equals):
    group = 'custom "display", A=B'
    arguments = [
        "tiger_train.sh", "--data-dir", "data/beauty", "--semantic-id-path", "semantic.pt",
        "--group", "rvq", "--notes", "display test",
        *(["--wandb-group=" + group] if equals else ["--wandb-group", group]),
    ]
    command = 'uv() { printf "%s\\n" "$@"; }; export -f uv; bash ' + shlex.join(arguments)
    result = subprocess.run([bash], input=command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    argv = result.stdout.splitlines()
    marker = argv.index("src.main")
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        cfg = compose(config_name="main", overrides=argv[marker + 1 :])
    assert cfg.sid_type == "rvq" and cfg.logger.wandb.group == group
    assert cfg.run_display_name == "tiger_beauty_seed42_rvq_train"


@pytest.mark.parametrize("script", ["sem_embeds_inference.sh", "tiger_train.sh", "intrr_train.sh"])
def test_legacy_optional_dataset_name_survives_real_script_and_compose(bash, script):
    arguments = [script, "--data-dir", "data/legacy_folder", "+dataset_name=home_and_kitchen"]
    if script != "sem_embeds_inference.sh":
        arguments += ["--semantic-id-path", "semantic.pt", "--group", "rkmeans", "--notes", "legacy metadata"]
    command = 'uv() { printf "%s\\n" "$@"; }; export -f uv; bash ' + shlex.join(arguments)
    result = subprocess.run([bash], input=command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    argv = result.stdout.splitlines()
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        cfg = compose(config_name="main", overrides=argv[argv.index("src.main") + 1 :])
    assert cfg.data_dir == "data/legacy_folder"
    assert cfg.dataset_name == cfg.display_dataset_name == "home_and_kitchen"
    assert "_home_and_kitchen_seed42_" in cfg.logger.wandb.name


@pytest.mark.parametrize("experiment", ["sem_embeds_inference", "tiger_train", "intrr_train", "rkmeans_train"])
def test_display_dataset_fallback_does_not_reserve_optional_metadata_key(experiment):
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        cfg = compose(config_name="main", overrides=[f"experiment={experiment}", "data_dir=data/steam"])
    assert "dataset_name" not in cfg
    assert cfg.display_dataset_name == "steam"
