"""用本地最小 bundle 验证 hybrid hits 的来源协议边界，不访问 W&B。"""

import pytest
import torch

import src.data.components.artifacts as artifacts
from src.utils.wandb import ResolvedArtifactReference

NAMES = ("full", "no_mixture", "no_residual", "no_joint_ce")
PROTOCOL = "copmrec-hybrid-deployment-v1"


def deployment(name):
    return dict(
        protocol=PROTOCOL,
        mode="hybrid",
        generation_candidates=20,
        candidate_strategy="probability_mixture",
        candidate_pool="beam_plus_all_cold",
        final_score="joint_catalog_logits",
        rank_ties="stable_catalog_row",
        history_exclusion=False,
        alpha_policy="frozen_0.5" if name == "no_mixture" else "learned",
        alpha_source="fixed" if name == "no_mixture" else "checkpoint",
        fixed_mixture_alpha=0.5 if name == "no_mixture" else None,
    )


@pytest.fixture
def resolved_bundles(monkeypatch, tmp_path):
    bundle = tmp_path / "predictions.pt"
    torch.save({"keys": torch.tensor([2, 1]), "predictions": torch.zeros(2, 10, 4, dtype=torch.long)}, bundle)
    contracts = {name: deployment(name) for name in NAMES}
    registry = artifacts.get_resolved_artifact_registry()
    registry.clear()

    def resolve(**kwargs):
        name = kwargs["uri"].run_id
        return ResolvedArtifactReference(
            field_name=kwargs["field_name"],
            original_uri=kwargs["uri"].original_uri,
            resolved_path=str(bundle),
            producer_run_id=name,
            entity="fixture",
            project="GRID",
            artifact_name=f"{name}:v0",
            artifact_version="v0",
            artifact_type="recommendation_output",
            artifact_path=f"fixture/GRID/{name}:v0",
            role="recommendation_output",
            file="merged_predictions_tensor.pt",
            metadata={"deployment_contract": contracts[name]},
        )

    monkeypatch.setattr(artifacts, "resolve_wandb_artifact", resolve)
    yield bundle, contracts
    registry.clear()


def load_hybrid():
    return artifacts.load_m3_prediction_bundles(
        {name: f"wandb://fixture/GRID/{name}?role=recommendation_output&alias=v0" for name in NAMES},
        "hits",
        expected_deployment_protocol=PROTOCOL,
    )


def test_hybrid_hits_preserves_verified_metadata_and_sorted_keys(resolved_bundles):
    _, contracts = resolved_bundles
    outputs = load_hybrid()
    assert set(outputs) == set(NAMES)
    for name, output in outputs.items():
        assert output.keys.tolist() == [1, 2]
        assert output.auxiliary["deployment_contract"] == contracts[name]


@pytest.mark.parametrize("fault", ["dense", "missing", "beam", "alpha", "history"])
def test_hybrid_hits_rejects_mixed_or_incomplete_artifact_deployment(resolved_bundles, fault):
    _, contracts = resolved_bundles
    if fault == "missing":
        contracts["no_mixture"] = None
    else:
        field, value = {
            "dense": ("mode", "dense"),
            "beam": ("generation_candidates", 10),
            "alpha": ("alpha_source", "checkpoint"),
            "history": ("history_exclusion", True),
        }[fault]
        contracts["no_mixture"][field] = value
    with pytest.raises(ValueError, match="no_mixture requires verified hybrid deployment"):
        load_hybrid()


def test_hybrid_hits_requires_artifact_metadata_while_legacy_dense_local_inputs_still_load(resolved_bundles):
    bundle, _ = resolved_bundles
    paths = {name: str(bundle) for name in NAMES}
    with pytest.raises(ValueError, match="verified hybrid deployment Artifact metadata"):
        artifacts.load_m3_prediction_bundles(paths, "hits", expected_deployment_protocol=PROTOCOL)
    outputs = artifacts.load_m3_prediction_bundles(paths, "hits")
    assert set(outputs) == set(NAMES)
    assert all(output.auxiliary == {} for output in outputs.values())


def test_residual_cannot_consume_hybrid_as_if_it_were_dense(resolved_bundles):
    with pytest.raises(ValueError, match="Only hybrid hits"):
        artifacts.load_m3_prediction_bundles({"full": "unused"}, "residual", expected_deployment_protocol=PROTOCOL)
    with pytest.raises(ValueError, match="cannot use hybrid output for legacy dense analysis"):
        artifacts.load_m3_prediction_bundles(
            {"full": "wandb://fixture/GRID/full?role=recommendation_output"}, "residual"
        )


def test_explicit_dense_artifact_remains_compatible_with_legacy_analysis(resolved_bundles):
    _, contracts = resolved_bundles
    contracts["full"].update(mode="dense", candidate_pool="all_catalog")
    output = artifacts.load_m3_prediction_bundles(
        {"full": "wandb://fixture/GRID/full?role=recommendation_output"}, "residual"
    )
    assert output["full"].keys.tolist() == [1, 2]
