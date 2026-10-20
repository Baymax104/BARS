"""冻结预测SHA与Artifact实际部署身份的CPU验证，不访问外部服务。"""

import hashlib
from types import SimpleNamespace

import pytest
import torch

from src.data.components import artifacts


@pytest.fixture(autouse=True)
def isolated_registry(monkeypatch):
    registry = artifacts.ResolvedArtifactRegistry()
    monkeypatch.setattr(artifacts, "get_resolved_artifact_registry", lambda: registry)


@pytest.fixture
def prediction_file(tmp_path):
    path = tmp_path / "predictions.pt"
    torch.save({"keys": torch.tensor([8, 2]), "predictions": torch.tensor([[80], [20]])}, path)
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_audited_local_prediction_keeps_identity_and_key_order(prediction_file):
    path, digest = prediction_file
    result = artifacts.load_audited_prediction_output(str(path), digest)
    assert result.keys.tolist() == [2, 8]
    assert result.predictions.tolist() == [[20], [80]]
    assert result.auxiliary["source_reference"] == str(path)
    assert result.auxiliary["source_sha256"] == digest
    assert result.auxiliary["source_metadata"] == {}
    assert artifacts.load_model_output(str(path)).keys.tolist() == [2, 8]


@pytest.mark.parametrize("digest", [None, "", "X" * 64, "a" * 63, "0" * 64])
def test_prediction_hash_mismatch_or_invalid_rejected(prediction_file, digest):
    path, _ = prediction_file
    with pytest.raises(ValueError, match="SHA256"):
        artifacts.load_audited_prediction_output(str(path), digest)


@pytest.mark.parametrize("invalid", [None, {}, {"history_exclusion": 0}])
def test_expected_metadata_requires_actual_identity(prediction_file, monkeypatch, invalid):
    path, digest = prediction_file
    uri = "wandb://fixture/GRID/testing?role=recommendation_output&alias=v0"
    registry = artifacts.get_resolved_artifact_registry()

    def resolve(reference, field_name, **kwargs):
        registry.add(
            SimpleNamespace(
                original_uri=reference,
                field_name=field_name,
                metadata={"deployment_contract": invalid} if invalid is not None else {},
            )
        )
        return str(path)

    monkeypatch.setattr(artifacts, "resolve_reference", resolve)
    with pytest.raises(ValueError, match="deployment Artifact metadata"):
        artifacts.load_audited_prediction_output(uri, digest, {"history_exclusion": False})


def test_actual_artifact_deployment_metadata_is_preserved(prediction_file, monkeypatch):
    path, digest = prediction_file
    uri = "wandb://fixture/GRID/testing?role=recommendation_output&alias=v0"
    contract = {"protocol": "copmrec-hybrid-deployment-v1", "history_exclusion": False}
    registry = artifacts.get_resolved_artifact_registry()

    def resolve(reference, field_name, **kwargs):
        registry.add(
            SimpleNamespace(
                original_uri=reference,
                field_name=field_name,
                metadata={"deployment_contract": dict(contract), "original_variant": "no_residual"},
            )
        )
        return str(path)

    monkeypatch.setattr(artifacts, "resolve_reference", resolve)
    result = artifacts.load_audited_prediction_output(uri, digest, contract)
    assert result.auxiliary["deployment_contract"] == contract
    assert result.auxiliary["source_metadata"]["original_variant"] == "no_residual"


def test_audited_bundle_names_must_match(prediction_file):
    path, digest = prediction_file
    with pytest.raises(ValueError, match="names must match"):
        artifacts.load_audited_prediction_bundles({"untied": str(path)}, {"shared": digest})
    result = artifacts.load_audited_prediction_bundles({"untied": str(path)}, {"untied": digest})
    assert result["untied"].auxiliary["source_sha256"] == digest
