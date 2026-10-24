"""临时双残差 alpha=1 对照的精确端点、训练身份和入口装配。"""

import copy

import pytest
import torch
from bars_fixtures import bars, snapshot
from test_bars_untied_residual import checkpoint, optimizers, residual_weights, update
from test_liger import batch

VARIANT = "untied_fixed_alpha_one"


def test_exact_content_endpoint_keeps_untied_initialization_and_both_residual_gradients():
    options = dict(initialization_seed=200, dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(200)
    learned = bars("untied_residual", **options)
    learned_rng = torch.get_rng_state()
    torch.manual_seed(200)
    fixed = bars(VARIANT, **options)
    assert torch.equal(torch.get_rng_state(), learned_rng)
    torch.testing.assert_close(fixed.state_dict(), learned.state_dict(), rtol=0, atol=0)
    catalog, history = residual_weights(fixed)
    assert catalog.data_ptr() != history.data_ptr()
    assert not torch.count_nonzero(catalog) and not torch.count_nonzero(history)
    assert fixed.effective_mixture_alpha().item() == 1.0
    assert not fixed.effective_mixture_alpha().requires_grad
    assert not fixed.dynamic_gate.bias.requires_grad

    generation = torch.tensor([[-1000.0], [0.0]], requires_grad=True)
    content = torch.tensor([[-0.7], [-2.3]], requires_grad=True)
    assert fixed.target_mixture_log_probs(generation, content) is content
    fixed.target_mixture_log_probs(generation, content).sum().backward()
    assert generation.grad is None and fixed.dynamic_gate.bias.grad is None
    processor = fixed.candidate_processor(torch.randn(2, 6))
    assert processor.alpha == 1.0 and processor.gate is None

    inputs, labels = batch()
    torch.manual_seed(100)
    learned_values = learned.losses(inputs, labels.target_ids, training=True)
    learned_rng = torch.get_rng_state()
    torch.manual_seed(100)
    values = fixed.losses(inputs, labels.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), learned_rng)
    for name in ("sid_loss", "content_loss"):
        torch.testing.assert_close(values[name], learned_values[name], rtol=0, atol=0)
    torch.testing.assert_close(values["mixture_loss"], values["content_loss"] / fixed.num_hierarchies)
    expected = values["sid_loss"] + (1 + 1 / fixed.num_hierarchies) * values["content_loss"]
    torch.testing.assert_close(values["loss"], expected)
    parameters = [p for p in fixed.parameters() if p.requires_grad]
    actual_gradients = torch.autograd.grad(values["loss"], parameters, retain_graph=True)
    expected_gradients = torch.autograd.grad(expected, parameters, retain_graph=True)
    for actual, expected_gradient in zip(actual_gradients, expected_gradients, strict=True):
        assert torch.isfinite(actual).all()
        torch.testing.assert_close(actual, expected_gradient, atol=2e-6, rtol=2e-5)
    values["loss"].backward()
    assert fixed.dynamic_gate.bias.grad is None
    for weight in (catalog, history):
        assert weight.grad is not None and torch.isfinite(weight.grad).all()
        assert weight.grad[fixed.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight.grad[~fixed.seen_mask])


def test_independent_tables_keep_optimizer_group_and_own_continuous_restore():
    torch.manual_seed(42)
    actual = bars(VARIANT)
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
    assert saved["copmrec_alpha_policy"] == "frozen_1"
    assert saved["copmrec_fixed_mixture_alpha"] == 1.0
    assert saved["copmrec_formal_release"]["variant"] == VARIANT
    contract = saved["copmrec_unified_scratch"]
    assert contract["alpha_policy"] == "frozen_1"
    assert contract["residual_sharing"] == "untied_history_catalog"
    assert contract["loss_weights"] == {"sid_ce": 1, "joint_catalog_ce": 1, "mixture_nll": 1}
    assert contract["m3_ablation"]["variant"] == VARIANT

    restored = bars(VARIANT)
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
    bars(VARIANT).on_load_checkpoint(checkpoint(restored, restored_optimizer, restored_scheduler, 3))


@pytest.mark.parametrize("other", [None, "fixed_alpha_one", "untied_residual", "untied_no_joint_ce"])
def test_checkpoint_identity_rejects_existing_variants_in_both_directions(other):
    _, saved = snapshot(VARIANT)
    _, other_saved = snapshot(other)
    with pytest.raises(ValueError):
        bars(other).on_load_checkpoint(saved)
    with pytest.raises(ValueError):
        bars(VARIANT).on_load_checkpoint(other_saved)


@pytest.mark.parametrize("fault", ["gate", "alpha_policy", "fixed_alpha", "variant"])
def test_restore_rejects_relabelled_endpoint_or_nonzero_gate(fault):
    _, saved = snapshot(VARIANT)
    if fault == "gate":
        saved["state_dict"]["dynamic_gate.bias"].fill_(0.1)
    elif fault == "alpha_policy":
        saved["copmrec_alpha_policy"] = "learned"
    elif fault == "fixed_alpha":
        saved["copmrec_fixed_mixture_alpha"] = 0.5
    else:
        saved["copmrec_formal_release"]["variant"] = "untied_residual"
    with pytest.raises(ValueError):
        bars(VARIANT).on_load_checkpoint(saved)
