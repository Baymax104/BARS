"""双残差固定半半混合保留两路监督、优化配方及独立恢复身份。"""

import copy

import pytest
import torch
from copmrec_fixtures import copmrec, snapshot
from test_copmrec_untied_residual import checkpoint, optimizers, residual_weights, update
from test_liger import batch

VARIANT = "untied_fixed_alpha_half"


def test_exact_half_mixture_keeps_both_probability_gradients_and_fixed_inference():
    actual = copmrec(VARIANT)
    assert actual.effective_mixture_alpha().item() == 0.5
    assert not actual.effective_mixture_alpha().requires_grad
    assert not actual.dynamic_gate.bias.requires_grad
    generation = torch.tensor([[-0.2], [-2.0]], requires_grad=True)
    content = torch.tensor([[-1.4], [-0.4]], requires_grad=True)
    mixed = actual.target_mixture_log_probs(generation, content)
    expected = ((generation.exp() + content.exp()) / 2).log()
    torch.testing.assert_close(mixed, expected)
    mixed.sum().backward()
    for branch in (generation, content):
        assert branch.grad is not None and torch.isfinite(branch.grad).all() and (branch.grad > 0).all()
    assert actual.dynamic_gate.bias.grad is None

    # 半半混合 NLL 对另一路的梯度随当前这一路变化，不能拆成独立 CE 的固定加权和。
    changed_generation = generation.detach().sub(2).requires_grad_()
    changed_content = content.detach().clone().requires_grad_()
    actual.target_mixture_log_probs(changed_generation, changed_content).sum().backward()
    assert not torch.allclose(changed_content.grad, content.grad)
    assert not torch.allclose(-mixed, -(generation + content) / 2)
    processor = actual.candidate_processor(torch.randn(2, 6))
    assert processor.alpha == 0.5 and processor.gate is None
    prefix, scores = torch.zeros(2, 1, dtype=torch.long), torch.randn(2, 7)
    _, gen, mass, _ = processor.distributions(prefix, scores)
    torch.testing.assert_close(processor(prefix, scores)[:, 1:4], actual.target_mixture_log_probs(gen, mass))


def test_half_preserves_untied_initialization_rng_and_three_losses_with_both_residual_gradients():
    options = dict(initialization_seed=200, dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(200)
    learned = copmrec("untied_residual", **options)
    learned_rng = torch.get_rng_state()
    torch.manual_seed(200)
    fixed = copmrec(VARIANT, **options)
    assert torch.equal(torch.get_rng_state(), learned_rng)
    torch.testing.assert_close(fixed.state_dict(), learned.state_dict(), rtol=0, atol=0)
    catalog, history = residual_weights(fixed)
    assert catalog.data_ptr() != history.data_ptr()
    assert not torch.count_nonzero(catalog) and not torch.count_nonzero(history)

    inputs, labels = batch()
    torch.manual_seed(100)
    learned_values = learned.losses(inputs, labels.target_ids, training=True)
    learned_rng = torch.get_rng_state()
    torch.manual_seed(100)
    values = fixed.losses(inputs, labels.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), learned_rng)
    for name in ("sid_loss", "content_loss", "mixture_loss", "loss"):
        torch.testing.assert_close(values[name], learned_values[name])
    torch.testing.assert_close(values["loss"], values["sid_loss"] + values["content_loss"] + values["mixture_loss"])
    assert not torch.allclose(values["mixture_loss"], values["content_loss"] / fixed.num_hierarchies)
    assert not torch.allclose(values["mixture_loss"], values["sid_loss"])
    values["mixture_loss"].backward()
    assert fixed.transformer.decoder.block[0].layer[0].SelfAttention.q.weight.grad.abs().sum() > 0
    assert fixed.dynamic_gate.bias.grad is None
    for weight in (catalog, history):
        assert weight.grad is not None and torch.isfinite(weight.grad).all()
        assert weight.grad[fixed.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight.grad[~fixed.seen_mask])


def test_half_optimizer_freezes_gate_and_own_restore_preserves_next_update():
    torch.manual_seed(42)
    actual = copmrec(VARIANT)
    optimizer, scheduler = optimizers(actual)
    weights = residual_weights(actual)
    assert [group["initial_lr"] for group in optimizer.param_groups] == [0.0003, 0.002]
    assert len(optimizer.param_groups[1]["params"]) == 2
    assert all(p is not actual.dynamic_gate.bias for group in optimizer.param_groups for p in group["params"])
    for weight in weights:
        assert any(p is weight for p in optimizer.param_groups[1]["params"])
        assert all(p is not weight for p in optimizer.param_groups[0]["params"])
    for _ in range(2):
        update(actual, optimizer, scheduler)
    for weight in weights:
        assert weight[actual.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight[~actual.seen_mask])
        assert optimizer.state[weight]["step"].item() == 2
    assert not torch.count_nonzero(actual.dynamic_gate.bias)
    saved = checkpoint(actual, optimizer, scheduler, 2)
    assert saved["copmrec_alpha_policy"] == "frozen_0.5"
    assert saved["copmrec_fixed_mixture_alpha"] == 0.5
    assert saved["copmrec_formal_release"]["variant"] == VARIANT
    contract = saved["copmrec_unified_scratch"]
    assert contract["alpha_policy"] == "frozen_0.5"
    assert contract["residual_sharing"] == "untied_history_catalog"
    assert contract["loss_weights"] == {"sid_ce": 1, "joint_catalog_ce": 1, "mixture_nll": 1}
    assert contract["m3_ablation"]["variant"] == VARIANT

    restored = copmrec(VARIANT)
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    restored_optimizer, restored_scheduler = optimizers(restored)
    restored_optimizer.load_state_dict(copy.deepcopy(saved["optimizer_states"][0]))
    restored_scheduler.load_state_dict(copy.deepcopy(saved["lr_schedulers"][0]))
    assert restored.restored_step == 2
    update(actual, optimizer, scheduler)
    update(restored, restored_optimizer, restored_scheduler)
    torch.testing.assert_close(restored.state_dict(), actual.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_optimizer.state_dict(), optimizer.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_scheduler.state_dict(), scheduler.state_dict(), rtol=0, atol=0)
    copmrec(VARIANT).on_load_checkpoint(checkpoint(restored, restored_optimizer, restored_scheduler, 3))


@pytest.mark.parametrize("other", [None, "no_mixture", "fixed_alpha_one", "untied_residual", "untied_fixed_alpha_one"])
def test_half_checkpoint_identity_rejects_existing_variants_in_both_directions(other):
    _, saved = snapshot(VARIANT)
    _, other_saved = snapshot(other)
    with pytest.raises(ValueError):
        copmrec(other).on_load_checkpoint(saved)
    with pytest.raises(ValueError):
        copmrec(VARIANT).on_load_checkpoint(other_saved)


@pytest.mark.parametrize("fault", ["gate", "alpha_policy", "fixed_alpha", "bool_alpha", "variant"])
def test_half_restore_rejects_relabelled_alpha_or_nonzero_gate(fault):
    _, saved = snapshot(VARIANT)
    if fault == "gate":
        saved["state_dict"]["dynamic_gate.bias"].fill_(0.1)
    elif fault == "alpha_policy":
        saved["copmrec_alpha_policy"] = "learned"
    elif fault == "fixed_alpha":
        saved["copmrec_fixed_mixture_alpha"] = 1.0
    elif fault == "bool_alpha":
        saved["copmrec_fixed_mixture_alpha"] = True
    else:
        saved["copmrec_formal_release"]["variant"] = "untied_residual"
    with pytest.raises(ValueError):
        copmrec(VARIANT).on_load_checkpoint(saved)
