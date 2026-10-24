"""固定 checkpoint 诊断仅使用内存 CPU 模型，不运行 Trainer。"""

import copy
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest
import torch
from bars_fixtures import bars, snapshot
from test_liger import batch

from src.data.components.data_models import ModelOutput, TigerLabelData
from src.recommendation.bars.mechanism import (
    ARMS,
    CURRENT_VARIANT,
    LEGACY_MECHANISM_PROTOCOL,
    MECHANISM_PROTOCOL,
    BARSMechanismDiagnosis,
    candidate_decoder_scores,
)


def setup_diagnosis(variant=CURRENT_VARIANT, model_options=None, **overrides):
    source_options = {"validation_selection_mode": "hybrid"} if variant == CURRENT_VARIANT else {}
    source_options.update(model_options or {})
    original, checkpoint = snapshot(variant, **source_options)
    original.eval()
    x, _ = batch()
    predictions = original.retrieve(x)[0]
    reference = ModelOutput(
        keys=x.output_keys.flip(0),
        predictions=predictions.flip(0),
        auxiliary={
            "deployment_contract": original.deployment_contract,
            "source_sha256": "b" * 64,
        },
    )
    arguments = dict(
        backbone=bars(variant, **source_options),
        checkpoint=checkpoint,
        reference_predictions=reference,
        source_reference="toy-own-best.ckpt",
        source_sha256="a" * 64,
        prediction_reference="toy-frozen-predictions.pt",
        generation_candidates=original.generation_candidates,
        top_k=original.top_k,
        bootstrap_repetitions=12,
        candidate_score_batch_size=2,
    )
    arguments.update(overrides)
    diagnosis = BARSMechanismDiagnosis(**arguments)
    return diagnosis, original, checkpoint, diagnosis.reference_predictions


def start(diagnosis):
    diagnosis._trainer = SimpleNamespace(world_size=1)
    diagnosis.on_test_start()


def test_two_searches_four_arms_reproduce_production_and_do_not_mutate_checkpoint():
    diagnosis, original, checkpoint, reference = setup_diagnosis()
    saved = copy.deepcopy(checkpoint["state_dict"])
    start(diagnosis)
    with patch.object(
        diagnosis.backbone, "_generate_candidate_rows", wraps=diagnosis.backbone._generate_candidate_rows
    ) as generate:
        diagnosis.test_step(batch(), 0)
    assert generate.call_count == 2
    production = generate.call_args_list[0].kwargs["processor"]
    assert production.gate is None and production.alpha == 0.5
    endpoint = generate.call_args_list[1].kwargs["processor"]
    assert endpoint.alpha == 0 and endpoint.gate is None
    payload = diagnosis.structured_analysis_output()
    assert payload.metadata["protocol"] == MECHANISM_PROTOCOL
    assert payload.metadata["training_updates"] == 0
    assert payload.metadata["evidence_kind"] == "fixed_checkpoint_intervention"
    assert payload.metadata["production_reproduced"]
    assert payload.metadata["prediction_sha256"] == "b" * 64
    assert payload.metadata["source_variant"] == CURRENT_VARIANT
    assert payload.metadata["source_alpha"] == payload.metadata["fixed_mixture_alpha"] == 0.5
    assert payload.metadata["alpha_policy"] == "frozen_0.5"
    assert "learned_alpha" not in payload.metadata
    assert payload.metadata["source_training_contract"]["training_validation"] == "hybrid_beam_plus_all_cold"
    assert payload.metadata["source_training_contract"]["loss_weights"] == {
        "sid_ce": 1, "joint_catalog_ce": 1, "mixture_nll": 0
    }
    assert set(payload.bundles) == {f"{arm}.pt" for arm in (*ARMS, "dense_catalog")}
    torch.testing.assert_close(payload.bundles["production_catalog.pt"]["predictions"], reference.predictions)
    for name, value in diagnosis.backbone.state_dict().items():
        torch.testing.assert_close(value, saved[name], rtol=0, atol=0)
    assert not any(parameter.requires_grad for parameter in diagnosis.backbone.parameters())
    assert not diagnosis.backbone.training
    torch.testing.assert_close(original.effective_mixture_alpha(), diagnosis.backbone.effective_mixture_alpha())


def test_complete_decoder_path_scores_are_chunk_invariant_and_score_all_cold_candidates():
    actual, _ = snapshot("untied_residual")
    actual.eval()
    x, _ = batch()
    encoded, mask, _ = actual.encode(x.input_ids, x.attention_mask)
    users = torch.tensor([0] * 6 + [1] * 6)
    rows = torch.arange(6).repeat(2)
    together = candidate_decoder_scores(actual, encoded, mask, users, rows, batch_size=12)
    chunked = candidate_decoder_scores(actual, encoded, mask, users, rows, batch_size=1)
    torch.testing.assert_close(together, chunked, rtol=1e-6, atol=1e-6)
    assert torch.isfinite(together.reshape(2, 6)[:, ~actual.seen_mask]).all()
    # 本例六个完整 SID 穷尽合法目录，合法 decoder 路径概率总和应为 1。
    torch.testing.assert_close(together.reshape(2, 6).exp().sum(1), torch.ones(2), rtol=1e-6, atol=1e-6)
    user0_tokens = actual.semantic_ids[:1] + actual.offsets
    with patch.object(actual.transformer, "forward", wraps=actual.transformer.forward) as forward:
        candidate_decoder_scores(actual, encoded, mask, users[:1], rows[:1], batch_size=1)
    passed = forward.call_args.kwargs
    torch.testing.assert_close(passed["encoder_outputs"].last_hidden_state, encoded.last_hidden_state[:1])
    assert passed["encoder_outputs"].last_hidden_state.shape[1] > 1
    torch.testing.assert_close(passed["labels"], user0_tokens)


def test_fixed_pools_include_all_cold_and_both_rankers_share_the_same_candidates():
    diagnosis, _, _, reference = setup_diagnosis()
    start(diagnosis)
    generated = (torch.tensor([[0, 0, -1], [1, 2, 2]]), torch.tensor([[1, 2, -1], [0, 1, -1]]))
    logits = torch.tensor([[3.0, 99.0, 1.0, 1.0, 3.0, 3.0], [0.0, 6.0, 99.0, 1.0, 8.0, 7.0]])
    # production pool: 用户0=[0,4,5]，用户1=[1,2,4,5]。
    reference.predictions = diagnosis.backbone.semantic_ids[torch.tensor([[0, 4, 5], [2, 4, 5]])]
    observed = {}

    def score(model, encoded, mask, users, rows, *, batch_size):
        observed["pairs"] = list(zip(users.tolist(), rows.tolist(), strict=True))
        # 目录小行优先，独立于真实标签。
        return -rows.float()

    with (
        patch.object(diagnosis.backbone, "_generate_candidate_rows", side_effect=generated),
        patch.object(diagnosis.backbone, "dense_logits", return_value=logits),
        patch("src.recommendation.bars.mechanism.candidate_decoder_scores", side_effect=score),
    ):
        diagnosis.test_step(batch(), 0)
    assert all((user, cold) in observed["pairs"] for user in (0, 1) for cold in (4, 5))
    rows = {arm: [row for row in diagnosis.rows if row["variant"] == arm] for arm in ARMS}
    for generation in ("production", "alpha0"):
        for left, right in zip(rows[f"{generation}_catalog"], rows[f"{generation}_decoder"], strict=True):
            assert left["candidate_count"] == right["candidate_count"]
            assert left["target_covered"] == right["target_covered"]
            assert left["target_generated"] == right["target_generated"]
    assert rows["production_catalog"][0]["candidate_count"] == 3
    assert rows["production_catalog"][0]["invalid_generated_count"] == 1
    assert not rows["production_catalog"][0]["target_generated"]
    # 高分未生成 seen 行1没有混入用户0的候选。
    actual_rows = diagnosis.backbone.lookup_rows(torch.cat(diagnosis.predictions["production_catalog"]))
    assert actual_rows[0].tolist() == [0, 4, 5]
    comparisons = diagnosis.structured_analysis_output().documents["summary.json"]["comparisons"]
    expected_difference = -0.5 / np.log2(3)
    ranking = next(
        row
        for row in comparisons
        if row["comparison"] == "ranking_at_alpha0" and row["metric"] == "ndcg@10" and "category" not in row
    )
    interaction = next(
        row
        for row in comparisons
        if row["comparison"] == "generation_ranking_interaction" and row["metric"] == "ndcg@10"
    )
    assert np.isclose(ranking["difference"], expected_difference)
    assert np.isclose(interaction["difference"], -expected_difference)


def test_labels_only_change_measurements_and_never_candidates_or_scores():
    diagnosis, _, _, _ = setup_diagnosis()
    start(diagnosis)
    x, _ = batch()
    diagnosis.test_step(batch(), 0)
    expected = {arm: values[0].clone() for arm, values in diagnosis.predictions.items()}
    start(diagnosis)
    changed = TigerLabelData(torch.tensor([[0, 0], [2, 1]]))
    diagnosis.test_step((x, changed), 0)
    for arm in (*ARMS, "dense_catalog"):
        torch.testing.assert_close(diagnosis.predictions[arm][0], expected[arm], rtol=0, atol=0)


def test_statistics_pair_same_users_and_ndcg_contributions_sum_to_differences():
    diagnosis, _, _, _ = setup_diagnosis()
    start(diagnosis)
    diagnosis.test_step(batch(), 0)
    comparisons = diagnosis.structured_analysis_output().documents["summary.json"]["comparisons"]
    for name in (
        "generation_at_catalog",
        "generation_at_decoder",
        "ranking_at_production",
        "ranking_at_alpha0",
        "both_at_production",
    ):
        for k in (5, 10):
            selected = [row for row in comparisons if row["comparison"] == name and row["metric"] == f"ndcg@{k}"]
            main = next(row for row in selected if "category" not in row)
            components = [row for row in selected if "category" in row]
            assert len(components) == 4
            assert sum(row["count"] for row in components) == 2
            assert np.isclose(sum(row["contribution"] for row in components), main["difference"])
            assert main["ci_low"] <= main["difference"] <= main["ci_high"]
    interaction = [row for row in comparisons if row["comparison"] == "generation_ranking_interaction"]
    assert len(interaction) == 4


@pytest.mark.parametrize("fault", ["duplicate", "missing", "extra", "wrong_prediction"])
def test_reference_reproduction_and_exact_user_population_are_required(fault):
    diagnosis, _, _, _ = setup_diagnosis()
    start(diagnosis)
    if fault == "wrong_prediction":
        diagnosis.reference_predictions.predictions = diagnosis.reference_predictions.predictions.roll(1, 1)
        with pytest.raises(ValueError, match="exactly reproduce"):
            diagnosis.test_step(batch(), 0)
        return
    diagnosis.test_step(batch(), 0)
    if fault == "duplicate":
        diagnosis.keys.append(diagnosis.keys[0])
    elif fault == "missing":
        diagnosis.keys[0] = diagnosis.keys[0][:1]
    else:
        diagnosis.keys[0] = torch.tensor([11, 12, 999])
    with pytest.raises(ValueError, match="user"):
        diagnosis.structured_analysis_output()


@pytest.mark.parametrize("fault", ["shared", "missing_table", "seed", "deployment", "sha", "budget", "dense_source"])
def test_wrong_source_or_deployment_is_rejected(fault):
    _, original, checkpoint, reference = setup_diagnosis()
    arguments = {}
    if fault == "shared":
        arguments["backbone"] = bars()
    elif fault == "missing_table":
        del checkpoint["state_dict"]["history_collaborative_residual.weight"]
        arguments["checkpoint"] = checkpoint
    elif fault == "seed":
        arguments["backbone"] = bars(CURRENT_VARIANT, validation_selection_mode="hybrid", initialization_seed=43)
    elif fault == "deployment":
        reference.auxiliary["deployment_contract"] = {**original.deployment_contract, "history_exclusion": True}
        arguments["reference_predictions"] = reference
    elif fault == "sha":
        arguments["source_sha256"] = "wrong"
    elif fault == "dense_source":
        arguments["backbone"] = bars(CURRENT_VARIANT)
    else:
        arguments["generation_candidates"] = 20
    with pytest.raises((ValueError, RuntimeError)):
        setup_diagnosis(**arguments)


def test_multi_process_and_invalid_batch_are_rejected():
    diagnosis, _, _, _ = setup_diagnosis()
    diagnosis._trainer = SimpleNamespace(world_size=2)
    with pytest.raises(ValueError, match="single process"):
        diagnosis.on_test_start()
    start(diagnosis)
    with pytest.raises(ValueError, match="labels"):
        diagnosis.test_step((batch()[0], None), 0)


@pytest.mark.parametrize(
    "options",
    [
        {"num_hierarchies": 4},
        {"input_references": {"dataset": "toys", "training_seed": 42}},
        {"input_references": {"dataset": "beauty", "training_seed": 2026}},
    ],
)
def test_preprocessing_depth_and_stage_scope_must_match(options):
    with pytest.raises(ValueError, match="depths|Beauty/seed42"):
        setup_diagnosis(**options)


def test_explicit_historical_source_keeps_learned_gate_and_original_protocol():
    diagnosis, _, _, reference = setup_diagnosis(variant="untied_residual")
    start(diagnosis)
    with patch.object(
        diagnosis.backbone, "_generate_candidate_rows", wraps=diagnosis.backbone._generate_candidate_rows
    ) as generate:
        diagnosis.test_step(batch(), 0)
    assert generate.call_count == 2
    assert generate.call_args_list[0].kwargs["processor"].gate is diagnosis.backbone.dynamic_gate
    output = diagnosis.structured_analysis_output()
    assert output.metadata["protocol"] == LEGACY_MECHANISM_PROTOCOL
    assert output.metadata["reference_arm"] == "learned_catalog"
    assert output.metadata["source_variant"] == "untied_residual"
    assert output.metadata["alpha_policy"] == "learned"
    assert output.metadata["fixed_mixture_alpha"] is None
    assert output.metadata["learned_alpha"] == output.metadata["source_alpha"]
    torch.testing.assert_close(output.bundles["learned_catalog.pt"]["predictions"], reference.predictions, rtol=0, atol=0)


def test_current_full_beam20_top10_is_reproduced_exactly_for_each_business_user():
    sids = torch.cartesian_prod(torch.arange(5), torch.arange(5))
    options = dict(
        catalog=dict(
            keys=torch.arange(25) + 100,
            semantic_ids=sids,
            embeddings=torch.arange(125).reshape(25, 5).float() / 125,
            seen_mask=torch.arange(25) < 20,
        ),
        codebook_size=5,
        generation_candidates=20,
        top_k=10,
    )
    diagnosis, _, checkpoint, reference = setup_diagnosis(model_options=options)
    saved = copy.deepcopy(checkpoint["state_dict"])
    start(diagnosis)
    diagnosis.test_step(batch(), 0)
    output = diagnosis.structured_analysis_output()
    production = output.bundles["production_catalog.pt"]
    assert production["predictions"].shape == (2, 10, 2)
    assert torch.equal(production["keys"], reference.keys)
    assert torch.equal(production["predictions"], reference.predictions)
    assert output.metadata["generation_candidates"] == 20 and output.metadata["top_k"] == 10
    for name, value in diagnosis.backbone.state_dict().items():
        assert torch.equal(value, saved[name])
