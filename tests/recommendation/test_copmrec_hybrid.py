"""主部署使用 hybrid；旧训练身份和 dense 选优保持不变。"""

import copy
from unittest.mock import patch

import pytest
import torch
from copmrec_fixtures import copmrec, snapshot
from test_liger import batch

from src.recommendation.copmrec.ablation import TRAINING_VARIANTS


@pytest.mark.parametrize("variant", [None, *TRAINING_VARIANTS])
def test_existing_dense_checkpoint_restores_unchanged_for_both_deployments(variant):
    original, saved = snapshot(variant, prediction_mode="dense")
    original.eval()
    old_training_contract = copy.deepcopy(saved["copmrec_unified_scratch"])
    old_release = copy.deepcopy(saved["copmrec_formal_release"])
    expected_dense = original.retrieve(batch()[0])[0]
    restored = copmrec(variant, training_model_config=None).eval()
    assert restored.prediction_mode == "hybrid"
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    torch.testing.assert_close(restored.retrieve(batch()[0], "dense")[0], expected_dense)
    torch.testing.assert_close(restored.retrieve(batch()[0])[0], restored.retrieve(batch()[0], "hybrid")[0])
    assert restored.unified_scratch_contract == saved["copmrec_unified_scratch"] == old_training_contract
    assert saved["copmrec_formal_release"] == old_release
    assert old_training_contract["deployment"] == "raw_full_catalog_dense_without_history_exclusion"


def test_relabeling_saved_dense_training_contract_as_hybrid_is_rejected():
    _, saved = snapshot(prediction_mode="dense")
    saved["copmrec_unified_scratch"]["deployment"] = "hybrid"
    with pytest.raises(ValueError, match="origin/seed/continuous-budget"):
        copmrec().on_load_checkpoint(saved)


def test_hybrid_union_deduplicates_and_retains_history_without_dense_seen_fallback():
    actual = copmrec().eval()
    # 第一用户的0是历史商品；高分但未生成的seen行1不能混入候选。
    generated = torch.tensor([[0, 0, -1], [1, 4, -1]])
    logits = torch.tensor([[3.0, 99.0, 1.0, 1.0, 3.0, 3.0], [0.0, 6.0, 99.0, 1.0, 8.0, 7.0]])
    with (
        patch.object(actual, "generate_candidates", return_value=generated) as generate,
        patch.object(actual, "dense_logits", return_value=logits),
    ):
        sids, scores = actual.retrieve(batch()[0])
    torch.testing.assert_close(actual.lookup_rows(sids), torch.tensor([[0, 4, 5], [4, 5, 1]]))
    torch.testing.assert_close(scores, torch.tensor([[3.0, 3.0, 3.0], [8.0, 7.0, 6.0]]))
    assert torch.equal(generate.call_args.args[2], logits)


def test_validation_and_explicit_dense_never_generate_candidates():
    actual = copmrec().eval()
    logits = torch.tensor([[3.0, 99.0, 1.0, 1.0, 8.0, 7.0], [0.0, 6.0, 99.0, 1.0, 8.0, 7.0]])
    with (
        patch.object(actual, "generate_candidates", side_effect=AssertionError("dense must not generate")),
        patch.object(actual, "dense_logits", return_value=logits),
    ):
        dense = actual.retrieve(batch()[0], "dense")[0]
        validation = actual.eval_step(batch())["generated_ids"]
    expected_rows = torch.tensor([[1, 4, 5], [2, 4, 5]])
    torch.testing.assert_close(actual.lookup_rows(dense), expected_rows)
    torch.testing.assert_close(validation, dense)
    assert actual.evaluation_mode == "dense" and actual.prediction_mode == "hybrid"


@pytest.mark.parametrize(
    ("variant", "policy", "fixed"),
    [(None, "learned", None), ("no_mixture", "frozen_0.5", 0.5), ("fixed_alpha_one", "frozen_1", 1.0)],
)
def test_deployment_contract_and_processor_use_effective_alpha_policy(variant, policy, fixed):
    actual = copmrec(variant).eval()
    if variant is None:
        with torch.no_grad():
            actual.dynamic_gate.bias.fill_(2)
    processor = actual.candidate_processor(torch.zeros(2, 6))
    contract = actual.deployment_contract
    assert contract == dict(
        protocol="copmrec-hybrid-deployment-v1",
        mode="hybrid",
        generation_candidates=3,
        candidate_strategy="probability_mixture",
        candidate_pool="beam_plus_all_cold",
        final_score="joint_catalog_logits",
        rank_ties="stable_catalog_row",
        history_exclusion=False,
        alpha_policy=policy,
        alpha_source="fixed" if fixed is not None else "checkpoint",
        fixed_mixture_alpha=fixed,
    )
    if variant == "fixed_alpha_one":
        assert processor.alpha == 1 and processor.gate is None
        assert actual.effective_mixture_alpha().item() == 1
    else:
        assert processor.gate is actual.dynamic_gate
        assert actual.effective_mixture_alpha().item() == pytest.approx(
            0.5 if variant == "no_mixture" else torch.tensor(2.0).sigmoid().item()
        )
    assert actual.history_eligibility_contract["score_rule"] == "unchanged_candidate_joint_logits"
    dense = copmrec(variant, prediction_mode="dense")
    assert dense.deployment_contract["mode"] == "dense"
    assert dense.deployment_contract["candidate_pool"] == "all_catalog"
    assert dense.history_eligibility_contract["protocol"] == "copmrec-final-history-exclusion-off-v1"


@pytest.mark.parametrize(
    "options",
    [dict(prediction_mode="generative"), dict(evaluation_mode="hybrid"), dict(candidate_trace=True)],
)
def test_unsupported_deployment_or_selection_controls_remain_rejected(options):
    with pytest.raises(ValueError, match="dense selection"):
        copmrec(**options)


def test_retrieve_rejects_generative_or_target_conditioned_prediction():
    actual = copmrec().eval()
    with pytest.raises(ValueError, match="dense/hybrid"):
        actual.retrieve(batch()[0], "generative")
    with pytest.raises(ValueError, match="without target traces"):
        actual.retrieve(batch()[0], "hybrid", target_ids=batch()[1].target_ids)
