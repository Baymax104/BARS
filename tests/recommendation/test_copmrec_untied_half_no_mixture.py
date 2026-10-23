"""固定半半推理，训练仅保留 SID CE 与目录 CE。"""

import pytest
import torch
from copmrec_fixtures import copmrec, snapshot
from test_copmrec_untied_residual import optimizers, residual_weights, update
from test_liger import batch

VARIANT = "untied_fixed_alpha_half_no_mixture"


def test_removal_preserves_initialization_rng_and_exact_two_loss_gradients():
    options = dict(dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(42)
    reference = copmrec("untied_fixed_alpha_half", **options)
    rng = torch.get_rng_state()
    torch.manual_seed(42)
    actual = copmrec(VARIANT, **options)
    assert torch.equal(torch.get_rng_state(), rng)
    torch.testing.assert_close(actual.state_dict(), reference.state_dict(), rtol=0, atol=0)
    inputs, labels = batch()
    torch.manual_seed(123)
    expected = reference.losses(inputs, labels.target_ids, training=True)
    rng = torch.get_rng_state()
    torch.manual_seed(123)
    values = actual.losses(inputs, labels.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), rng)
    for name in ("sid_loss", "content_loss", "mixture_loss"):
        torch.testing.assert_close(values[name], expected[name], rtol=0, atol=0)
    assert not values["mixture_loss"].requires_grad
    torch.testing.assert_close(values["loss"], values["sid_loss"] + values["content_loss"], rtol=0, atol=0)
    expected_gradients = torch.autograd.grad(
        expected["sid_loss"] + expected["content_loss"],
        [p for p in reference.parameters() if p.requires_grad],
    )
    values["loss"].backward()
    for parameter, gradient in zip(
        [p for p in actual.parameters() if p.requires_grad], expected_gradients, strict=True
    ):
        assert parameter.grad is not None and torch.isfinite(parameter.grad).all()
        torch.testing.assert_close(parameter.grad, gradient, rtol=0, atol=0)
    for weight in residual_weights(actual):
        assert weight.grad[actual.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight.grad[~actual.seen_mask])
    assert actual.dynamic_gate.bias.grad is None
    processor = actual.candidate_processor(torch.randn(2, 6))
    assert processor.alpha == 0.5 and processor.gate is None
    assert actual.effective_mixture_alpha().item() == 0.5


def test_own_checkpoint_preserves_two_losses_and_optimizer_continuity():
    actual, saved = snapshot(VARIANT, updates=2)
    assert saved["copmrec_unified_scratch"]["loss_weights"] == {
        "sid_ce": 1, "joint_catalog_ce": 1, "mixture_nll": 0
    }
    assert saved["copmrec_alpha_policy"] == "frozen_0.5"
    assert saved["copmrec_fixed_mixture_alpha"] == 0.5
    restored = copmrec(VARIANT)
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    optimizer, scheduler = optimizers(restored)
    optimizer.load_state_dict(saved["optimizer_states"][0])
    scheduler.load_state_dict(saved["lr_schedulers"][0])
    assert restored.restored_step == 2
    assert not any(p is restored.dynamic_gate.bias for group in optimizer.param_groups for p in group["params"])
    update(restored, optimizer, scheduler)
    for weight in residual_weights(restored):
        assert optimizer.state[weight]["step"].item() == 3
    assert restored.effective_mixture_alpha().item() == 0.5
    assert actual.ablation_contract == restored.ablation_contract


@pytest.mark.parametrize("other", [None, "no_mixture", "untied_residual", "untied_fixed_alpha_half"])
def test_checkpoint_cannot_be_relabelled_as_a_different_objective(other):
    _, saved = snapshot(VARIANT)
    _, old = snapshot(other)
    with pytest.raises(ValueError):
        copmrec(other).on_load_checkpoint(saved)
    with pytest.raises(ValueError):
        copmrec(VARIANT).on_load_checkpoint(old)
