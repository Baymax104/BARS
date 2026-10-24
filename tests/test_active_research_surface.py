from pathlib import Path

import pytest
from hydra import compose, initialize_config_dir
from hydra.errors import MissingConfigException

ROOT = Path(__file__).parents[1]

RETIRED_MODULE_PREFIXES = (
    "src.quantization.tail_sid_diagnosis",
    "src.recommendation.tiger.prefix_allocation",
    "src.data.components.prefix_trace",
    "src.data.catalog_diagnosis",
    "src.data.datamodule.diagnosis",
    "src.data.datamodule.tiger_trace",
    "src.recommendation.brir",
    "src.recommendation.tiger_catalog_grounded",
    "src.recommendation.tiger_item_resolution",
    "src.recommendation.tiger_training_probe",
    "src.recommendation.liger.dynamic_mixture",
    "src.recommendation.liger.gate_training",
    "src.recommendation.liger.learned_reranker",
    "src.recommendation.liger.paired_rerank",
    "src.recommendation.liger.preference_dispersion",
    "src.data.components.liger_gate",
    "src.data.components.liger_learned",
    "src.data.components.item_resolution",
)

RETIRED_LAUNCHERS = (
    "tail_sid_diagnosis",
    "tiger_prefix_trace",
    "tiger_prefix_allocation_probe",
    "brir",
    "tiger_catalog_grounded",
    "tiger_item_resolution",
    "tiger_training_probe",
    "liger_gate",
    "liger_learned",
    "liger_candidate_union",
    "liger_source_protection",
    "sid_partition_intervention",
    "sid_partition_probe",
)


def _active_text_files():
    for root, suffixes in (
        (ROOT / "src", {".py"}),
        (ROOT / "configs", {".yaml"}),
        (ROOT / "scripts", {".sh"}),
    ):
        yield from (path for path in root.rglob("*") if path.is_file() and path.suffix in suffixes)
    yield from ROOT.glob("*.sh")


def test_recommendation_packages_only_expose_current_methods():
    packages = {path.parent.name for path in (ROOT / "src" / "recommendation").glob("*/__init__.py")}

    assert packages == {"bars", "intrr", "letter", "liger", "sasrec", "tiger"}


def test_active_surface_has_no_retired_imports_or_hydra_targets():
    violations = []
    for path in _active_text_files():
        text = path.read_text(encoding="utf-8")
        for prefix in RETIRED_MODULE_PREFIXES:
            if prefix in text:
                violations.append(f"{path.relative_to(ROOT)}: {prefix}")

    assert violations == []


def test_retired_launchers_and_configs_are_absent():
    active_paths = [
        path.relative_to(ROOT).as_posix().lower()
        for root in (ROOT / "configs", ROOT / "scripts")
        for path in root.rglob("*")
        if path.is_file()
    ]
    active_paths.extend(path.name.lower() for path in ROOT.glob("*.sh"))

    violations = [path for path in active_paths if any(name in path for name in RETIRED_LAUNCHERS)]
    assert violations == []


@pytest.mark.parametrize("experiment", ["tail_sid_diagnosis", "tiger_prefix_trace", "tiger_prefix_allocation_probe"])
def test_retired_analysis_experiments_cannot_compose(experiment):
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        with pytest.raises(MissingConfigException, match=experiment):
            compose(config_name="main", overrides=[f"experiment={experiment}"])


def test_retired_analysis_modules_are_absent():
    modules = (
        "src/quantization/tail_sid_diagnosis/module.py",
        "src/recommendation/tiger/prefix_allocation.py",
        "src/data/components/prefix_trace.py",
        "src/data/catalog_diagnosis.py",
        "src/data/datamodule/diagnosis.py",
        "src/data/datamodule/tiger_trace.py",
    )
    assert all(not (ROOT / name).exists() for name in modules)
