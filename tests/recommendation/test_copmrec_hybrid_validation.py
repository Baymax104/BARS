"""验证真实hybrid选点候选行为与checkpoint选择来源隔离。"""

from unittest.mock import patch

import pytest
import torch
from copmrec_fixtures import copmrec, snapshot
from test_liger import batch

VARIANT = "untied_fixed_alpha_half_no_mixture"


def test_hybrid_validation_uses_generated_pool_cold_union_and_stable_catalog_scores():
    actual = copmrec(VARIANT, validation_selection_mode="hybrid").eval()
    generated = torch.tensor([[0, 0, -1], [1, 4, -1]])
    logits = torch.tensor([[3.0, 99.0, 1.0, 1.0, 3.0, 3.0], [0.0, 6.0, 99.0, 1.0, 8.0, 7.0]])
    with (
        torch.no_grad(),
        patch.object(actual, "generate_candidates", return_value=generated) as generate,
        patch.object(actual, "dense_logits", return_value=logits),
    ):
        values = actual.validation_step(batch(), 0)
        predicted, scores = actual.retrieve(batch()[0])
    expected = torch.tensor([[0, 4, 5], [4, 5, 1]])
    torch.testing.assert_close(actual.lookup_rows(values["generated_ids"]), expected)
    torch.testing.assert_close(values["generated_ids"], predicted)
    torch.testing.assert_close(values["marginal_probs"], scores)
    assert generate.call_count == 2
    assert actual.effective_mixture_alpha().item() == 0.5


def test_hybrid_checkpoint_keeps_selection_identity_and_rejects_dense_or_changed_candidates():
    _, saved = snapshot(VARIANT, validation_selection_mode="hybrid")
    contract = saved["copmrec_unified_scratch"]
    assert contract["training_validation"] == "hybrid_beam_plus_all_cold"
    assert contract["deployment"] == "hybrid_beam_plus_all_cold_without_history_exclusion"
    assert contract["validation_retrieval"]["candidate_pool"] == "beam_plus_all_cold"
    assert contract["validation_retrieval"]["generation_candidates"] == 3
    restored = copmrec(VARIANT, validation_selection_mode="hybrid", training_model_config=None)
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    assert restored.restored_step == 1
    with pytest.raises(ValueError, match="origin/seed/continuous-budget"):
        copmrec(VARIANT).on_load_checkpoint(saved)
    with pytest.raises(ValueError, match="origin/seed/continuous-budget"):
        copmrec(VARIANT, validation_selection_mode="hybrid", generation_candidates=2).on_load_checkpoint(saved)
    _, dense = snapshot(VARIANT)
    assert dense["copmrec_unified_scratch"]["training_validation"] == "raw_full_catalog_dense"
    assert "validation_retrieval" not in dense["copmrec_unified_scratch"]
    with pytest.raises(ValueError, match="origin/seed/continuous-budget"):
        restored.on_load_checkpoint(dense)


def test_evaluation_mode_cannot_disagree_with_checkpoint_selection_identity():
    with pytest.raises(ValueError, match="matching evaluation/selection"):
        copmrec(VARIANT, validation_selection_mode="hybrid", evaluation_mode="dense")
