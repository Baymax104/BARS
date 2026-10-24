"""工程名称与已落盘的科学协议身份分别核验。"""

import io
import tokenize
from pathlib import Path

import pytest
from hydra import compose, initialize_config_dir
from hydra.errors import MissingConfigException

from src.recommendation.bars import BARS
from src.recommendation.bars.ablation import BARSAblation

ROOT = Path(__file__).resolve().parents[1]


def test_python_identifiers_and_source_paths_use_bars():
    violations = []
    for folder in ("src", "tests"):
        for path in (ROOT / folder).rglob("*.py"):
            if "copmrec" in path.name.lower():
                violations.append(str(path.relative_to(ROOT)))
            for token in tokenize.generate_tokens(io.StringIO(path.read_text(encoding="utf-8")).readline):
                if token.type == tokenize.NAME and "copmrec" in token.string.lower():
                    violations.append(f"{path.relative_to(ROOT)}:{token.start[0]}:{token.string}")
    assert violations == []
    assert not (ROOT / "src/recommendation/copmrec").exists()
    assert BARS.__module__ == "src.recommendation.bars.module"
    assert BARSAblation.__module__ == "src.recommendation.bars.ablation"


def test_configs_and_root_scripts_use_bars():
    old_paths = [path for path in (ROOT / "configs").rglob("*.yaml") if "copmrec" in path.name.lower()]
    old_paths.extend(ROOT.glob("copmrec*.sh"))
    assert old_paths == []
    for name in ("bars_train", "bars_inference", "bars_ablation_train", "bars_ablation_inference", "bars_diagnosis"):
        assert (ROOT / f"{name}.sh").is_file()
        assert (ROOT / f"configs/experiment/{name}.yaml").is_file()


@pytest.mark.parametrize(
    "experiment",
    ["copmrec_train", "copmrec_inference", "copmrec_ablation_train", "copmrec_ablation_inference", "copmrec_diagnosis"],
)
def test_old_experiment_names_cannot_compose(experiment):
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base="1.3"):
        with pytest.raises(MissingConfigException, match=experiment):
            compose(config_name="main", overrides=[f"experiment={experiment}"])
