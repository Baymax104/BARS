"""冻结列表的精确指标、用户配对、贡献守恒与错误输入检查。"""

import copy
import math
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from omegaconf import OmegaConf

from src.data.components.data_models import ModelOutput, TigerLabelData
from src.recommendation.bars.contributions import METRIC_NAMES, BARSContributionDiagnosis


def catalog():
    return torch.cartesian_prod(torch.arange(4), torch.arange(4))


def sources():
    sids = catalog()
    result = {}
    rank_conditions = {
        "untied": {101: 1, 102: 0, 103: 6, 104: 2},
        "shared": {101: 3, 102: 2, 103: 0, 104: 1},
        "no_residual": {101: 0, 102: 0, 103: 0, 104: 0},
    }
    for name, ranks in rank_conditions.items():
        keys = torch.tensor([103, 101, 104, 102] if name == "untied" else [104, 102, 101, 103])
        predictions = []
        for key in keys.tolist():
            target = key - 101
            rows = [row for row in range(16) if row != target][:10]
            if ranks[key]:
                rows.insert(ranks[key] - 1, target)
                rows = rows[:10]
            predictions.append(sids[rows])
        result[name] = ModelOutput(
            keys, torch.stack(predictions), {"source_reference": f"frozen://{name}", "variant": name}
        )
    return result


def diagnosis(**kwargs):
    options = dict(prediction_bundles=sources(), semantic_ids=catalog(), num_hierarchies=2, bootstrap_repetitions=73)
    options.update(kwargs)
    model = BARSContributionDiagnosis(**options)
    model._trainer = SimpleNamespace(world_size=1)
    model.on_test_start()
    return model


def batch(keys):
    keys = torch.tensor(keys)
    # history 故意不提供：本分析只读取业务 key 与用于测量的 label。
    return SimpleNamespace(output_keys=keys), TigerLabelData(catalog()[keys - 101])


def measure(model):
    model.test_step(batch([104, 102]), 0)
    model.test_step(batch([101, 103]), 1)
    return model.structured_analysis_output()


def test_current_stage_protocol_does_not_relabel_prediction_source_identity():
    protocol = "bars-fixed-half-hybrid-m3-20261023-v1"
    output = measure(diagnosis(protocol=protocol))
    assert output.metadata["protocol"] == protocol
    assert output.metadata["prediction_source_metadata"]["no_residual"]["variant"] == "no_residual"


@pytest.mark.parametrize("references", [{"dataset": "sports"}, {"training_seed": 200}])
def test_references_cannot_change_current_mechanism_stage(references):
    with pytest.raises(ValueError, match="Beauty/seed42"):
        diagnosis(input_references=OmegaConf.create(references))


def test_keyed_metrics_direct_bootstrap_and_decomposition_are_exact():
    model = diagnosis(input_references=OmegaConf.create({"untied": "immutable-original-variant"}))
    assert list(model.parameters()) == [] and not hasattr(model, "backbone")
    output = measure(model)
    assert output.metadata["user_count"] == 4
    assert output.metadata["input_references"] == {"untied": "immutable-original-variant"}
    assert output.metadata["prediction_source_metadata"]["no_residual"]["variant"] == "no_residual"
    assert output.metadata["model_forward_count"] == output.metadata["optimizer_updates"] == 0
    assert output.metadata["difference_direction"] == "reference_minus_comparison"
    assert output.metadata["relative_change_denominator"] == "comparison"
    assert set(output.tables) == {"users.csv", "comparisons.csv", "cases.csv"}
    assert len(output.tables["users.csv"]) == 12

    def values(ranks):
        return np.array(
            [
                [
                    float(0 < rank <= k) if metric == "recall" else (1 / math.log2(rank + 1) if 0 < rank <= k else 0)
                    for k in (5, 10)
                    for metric in ("recall", "ndcg")
                ]
                for rank in ranks
            ]
        )

    ref = values([1, 0, 6, 2])
    other = values([3, 2, 0, 1])
    zero = np.zeros((4, 4))
    # 模块按名字排序比较，且所有比较/指标复用同一个用户抽样。
    delta = np.concatenate([ref - zero, ref - other], axis=1)
    rng = np.random.Generator(np.random.PCG64(42))
    expected = np.quantile(
        np.stack([delta[rng.integers(4, size=4)].mean(0) for _ in range(73)]), [0.025, 0.975], axis=0
    )
    pairs = [row for row in output.tables["comparisons.csv"] if row["metric"] in METRIC_NAMES]
    assert len(pairs) == 8
    for j, row in enumerate(pairs):
        assert row["metric"] == METRIC_NAMES[j % 4]
        assert row["reference"] == "untied"
        assert row["signed_difference"] == pytest.approx(delta[:, j].mean(), abs=1e-15)
        assert row["ci_low"] == pytest.approx(expected[0, j], abs=1e-15)
        assert row["ci_high"] == pytest.approx(expected[1, j], abs=1e-15)
        assert row["signed_difference"] == pytest.approx(
            sum(row[f"contribution_{name}"] for name in ("gain", "loss", "common_rank")), abs=1e-15
        )
        if row["comparison"] == "no_residual":
            assert row["relative_percent"] is None
        else:
            assert row["relative_percent"] == pytest.approx(100 * row["signed_difference"] / row["comparison_mean"])
    ndcg10 = next(row for row in pairs if row["comparison"] == "shared" and row["metric"] == "ndcg@10")
    assert ndcg10["contribution_gain"] == pytest.approx(1 / math.log2(7) / 4)
    assert ndcg10["contribution_loss"] == pytest.approx(-1 / math.log2(3) / 4)
    assert ndcg10["contribution_common_rank"] == pytest.approx(((1 - 0.5) + (1 / math.log2(3) - 1)) / 4)
    assert output.metadata == model.structured_analysis_output().metadata
    assert output.tables == model.structured_analysis_output().tables
    for name, bundle in output.bundles.items():
        assert torch.equal(bundle["keys"], torch.tensor([101, 102, 103, 104]))
        original = sources()[name.removesuffix(".pt")]
        order = original.keys.argsort()
        torch.testing.assert_close(bundle["predictions"], original.predictions[order], rtol=0, atol=0)


def test_labels_change_metrics_but_never_frozen_prediction_lists():
    original = measure(diagnosis())
    model = diagnosis()
    inputs, labels = batch([101, 102, 103, 104])
    labels.target_ids = catalog()[torch.tensor([12, 13, 14, 15])]
    model.test_step((inputs, labels), 0)
    changed = model.structured_analysis_output()
    assert changed.documents["summary.json"]["observations"] != original.documents["summary.json"]["observations"]
    torch.testing.assert_close(changed.bundles, original.bundles, rtol=0, atol=0)


def test_any_two_sources_and_reference_are_supported_without_legacy_shared_ablations():
    selected = {name: bundle for name, bundle in sources().items() if name in ("untied", "shared")}
    selected["untied_no_joint_ce"] = selected.pop("shared")
    output = measure(diagnosis(prediction_bundles=selected, reference="untied_no_joint_ce"))
    assert {row["reference"] for row in output.tables["comparisons.csv"]} == {"untied_no_joint_ce"}
    assert {row["comparison"] for row in output.tables["comparisons.csv"]} == {"untied"}


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate_key",
        "float_key",
        "extra_user",
        "missing_user",
        "float_sid",
        "short_top10",
        "duplicate_item",
        "illegal_sid",
        "condition_name",
    ],
)
def test_prediction_sources_fail_closed(fault):
    bundles = sources()
    source = bundles["shared"]
    if fault == "duplicate_key":
        source.keys[1] = source.keys[0]
    elif fault == "float_key":
        source.keys = source.keys.float()
    elif fault == "extra_user":
        source.keys[0] = 999
    elif fault == "missing_user":
        source.keys, source.predictions = source.keys[:-1], source.predictions[:-1]
    elif fault == "float_sid":
        source.predictions = source.predictions.float()
    elif fault == "short_top10":
        source.predictions = source.predictions[:, :-1]
    elif fault == "duplicate_item":
        source.predictions[0, 1] = source.predictions[0, 0]
    elif fault == "illegal_sid":
        source.predictions[0, 1, 0] = 999
    else:
        bundles["../shared"] = bundles.pop("shared")
    with pytest.raises(ValueError):
        diagnosis(prediction_bundles=bundles)


@pytest.mark.parametrize(
    "options",
    [
        dict(bootstrap_repetitions=0),
        dict(bootstrap_repetitions=True),
        dict(num_hierarchies=True),
        dict(reference="missing"),
        dict(prediction_bundles={}),
        dict(semantic_ids=catalog().float()),
        dict(semantic_ids=catalog()[:5]),
    ],
)
def test_constructor_requires_valid_sources_catalog_and_statistics(options):
    with pytest.raises(ValueError):
        diagnosis(**options)


def test_duplicate_catalog_is_rejected():
    sids = catalog()
    sids[1] = sids[0]
    with pytest.raises(ValueError, match="unique"):
        diagnosis(semantic_ids=sids)


def test_single_process_labels_and_complete_population_are_required():
    model = diagnosis()
    model._trainer.world_size = 2
    with pytest.raises(ValueError, match="one process"):
        model.on_test_start()
    model._trainer.world_size = 1
    with pytest.raises(ValueError, match="no testing"):
        model.structured_analysis_output()
    inputs, labels = batch([101, 102])
    with pytest.raises(ValueError, match="real labels"):
        model.test_step((inputs, None), 0)
    invalid = copy.deepcopy(labels)
    invalid.target_ids[0, 0] = 99
    with pytest.raises(ValueError, match="absent"):
        model.test_step((inputs, invalid), 0)
    with pytest.raises(KeyError, match="Missing keys"):
        model.test_step((SimpleNamespace(output_keys=torch.tensor([999])), TigerLabelData(catalog()[:1])), 0)
    model.test_step((inputs, labels), 0)
    with pytest.raises(ValueError, match="duplicate"):
        model.test_step((inputs, labels), 1)
    with pytest.raises(ValueError, match="populations"):
        model.structured_analysis_output()
    model.on_test_start()
    assert measure(model).metadata["user_count"] == 4
