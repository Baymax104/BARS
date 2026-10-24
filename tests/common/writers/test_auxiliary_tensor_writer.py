from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
import torch

from src.common.writers.auxiliary_tensor_writer import AuxiliaryTensorWriter
from src.common.writers.local_pickle_writer import LocalPickleWriter
from src.common.writers.wandb_artifact_writer import WandbArtifactWriter
from src.data.components.data_models import ModelOutput

SCHEMA_VERSION = "test_trace_v1"


def validate_trace(bundle):
    if bundle["keys"].unique().numel() != bundle["keys"].numel():
        raise ValueError("Duplicate keys")
    assert bundle["schema_version"] == SCHEMA_VERSION
    assert bundle["labels"].shape[0] == len(bundle["keys"])
    assert bundle["trace"]["score"].shape == bundle["labels"].shape


def make_output(keys: list[int]) -> ModelOutput:
    return ModelOutput(
        keys=torch.tensor(keys),
        predictions=torch.zeros((len(keys), 10, 2), dtype=torch.long),
        auxiliary={
            "test_trace": {
                "schema_version": SCHEMA_VERSION,
                "labels": torch.zeros((len(keys), 2), dtype=torch.long),
                "trace": {"score": torch.ones((len(keys), 2))},
                "metadata": {"data_split": "evaluation"},
            }
        },
    )


def test_auxiliary_writer_merges_keyed_trace_without_changing_standard_bundle(tmp_path):
    trace_dir = tmp_path / "trace"
    writer = AuxiliaryTensorWriter(
        output_dir=str(trace_dir), payload_name="test_trace", output_filename="test_trace.pt", validator=validate_trace
    )
    writer.global_rank = 0
    writer.buffer = [make_output([2]), make_output([1])]
    writer.flush_buffer()
    path, _ = writer._merge_files()

    trace = torch.load(path, weights_only=True)
    assert trace["keys"].tolist() == [1, 2]

    prediction_dir = tmp_path / "prediction"
    prediction_writer = LocalPickleWriter(str(prediction_dir))
    prediction_writer.global_rank = 0
    prediction_writer.buffer = [make_output([1])]
    prediction_writer.flush_buffer()
    prediction_writer._merge_files()
    standard_bundle = torch.load(prediction_dir / "merged_predictions_tensor.pt", weights_only=False)
    assert set(standard_bundle) == {"keys", "predictions"}


def test_wandb_prediction_writer_ignores_auxiliary_payload(tmp_path, monkeypatch):
    monkeypatch.setattr("src.common.writers.wandb_artifact_writer.sync_file", lambda _: None)
    writer = WandbArtifactWriter(
        output_dir=str(tmp_path),
        artifact_name="recommendations",
        artifact_type="recommendation_output",
        role="recommendation_output",
        task_name="tiger_test_trace",
    )
    writer.global_rank = 0
    writer.buffer = [make_output([1])]
    writer.flush_buffer()

    output_path = writer._merge_files()
    bundle = torch.load(output_path, weights_only=False)

    assert set(bundle) == {"keys", "predictions"}


def test_auxiliary_writer_rejects_duplicate_keys(tmp_path):
    writer = AuxiliaryTensorWriter(str(tmp_path), "test_trace", "test_trace.pt", validator=validate_trace)
    writer.global_rank = 0
    writer.buffer = [make_output([1]), make_output([1])]
    writer.flush_buffer()

    with pytest.raises(ValueError, match="Duplicate keys"):
        writer._merge_files()


def test_auxiliary_writer_local_mode_does_not_require_wandb(tmp_path):
    writer = AuxiliaryTensorWriter(str(tmp_path), "test_trace", "test_trace.pt", validator=validate_trace)
    writer.global_rank = 0
    writer.buffer = [make_output([1])]

    writer.on_predict_end(SimpleNamespace(global_rank=0), SimpleNamespace())

    assert (tmp_path / "test_trace.pt").is_file()


def test_auxiliary_writer_propagates_publication_failure(tmp_path, monkeypatch):
    writer = AuxiliaryTensorWriter(
        str(tmp_path),
        "test_trace",
        "test_trace.pt",
        publish_wandb=True,
        artifact_name="trace",
        artifact_type="test_trace",
        role="test_trace",
        validator=validate_trace,
    )
    writer.global_rank = 0
    writer.buffer = [make_output([1])]
    monkeypatch.setattr(writer, "_publish_file", lambda *args: (_ for _ in ()).throw(RuntimeError("publish failed")))

    with pytest.raises(RuntimeError, match="publish failed"):
        writer.on_predict_end(SimpleNamespace(global_rank=0), SimpleNamespace())


def test_auxiliary_writer_publishes_test_trace_with_logger_owned_run(tmp_path, monkeypatch):
    path = tmp_path / "test_trace.pt"
    path.write_bytes(b"trace")
    artifacts = []

    class FakeArtifact:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.references = []

        def add_reference(self, uri, name):
            self.references.append((uri, name))

    run = SimpleNamespace(log_artifact=lambda artifact, aliases: artifacts.append((artifact, aliases)))
    monkeypatch.setitem(sys.modules, "wandb", SimpleNamespace(Artifact=FakeArtifact))
    monkeypatch.setattr(
        "src.common.writers.auxiliary_tensor_writer.require_wandb_logger_run",
        lambda trainer, purpose: run,
    )
    writer = AuxiliaryTensorWriter(
        str(tmp_path),
        "test_trace",
        "test_trace.pt",
        publish_wandb=True,
        artifact_name="test-trace",
        artifact_type="test_trace",
        role="test_trace",
        validator=validate_trace,
    )

    writer._publish_file(
        SimpleNamespace(),
        str(path),
        {
            "schema_version": SCHEMA_VERSION,
            "data_split": "evaluation",
            "beam_width": 10,
            "checkpoint_reference": "wandb://checkpoint",
            "semantic_id_reference": "wandb://sid",
        },
    )

    artifact, aliases = artifacts[0]
    assert artifact.kwargs["type"] == "test_trace"
    assert artifact.kwargs["metadata"]["role"] == "test_trace"
    assert artifact.kwargs["metadata"]["schema_version"] == SCHEMA_VERSION
    assert artifact.references == [(path.resolve().as_uri(), "test_trace.pt")]
    assert aliases == ["latest"]
