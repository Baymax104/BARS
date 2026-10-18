"""固定 alpha=1 对照保留三项损失、初始化和独立恢复身份。"""

import copy

import pytest
import torch
from copmrec_fixtures import copmrec, snapshot
from test_liger import batch

from src.recommendation.copmrec.diagnosis import prefix_observations


def test_fixed_alpha_one_is_exact_content_probability_with_no_gate_gradient():
    actual = copmrec("fixed_alpha_one")
    generation = torch.tensor([[-1000.0], [0.0]], requires_grad=True)
    content = torch.tensor([[-0.7], [-2.3]], requires_grad=True)
    target = actual.target_mixture_log_probs(generation, content)
    assert target is content
    target.sum().backward()
    assert generation.grad is None and actual.dynamic_gate.bias.grad is None
    assert actual.effective_mixture_alpha().item() == 1.0
    assert not actual.effective_mixture_alpha().requires_grad
    processor = actual.candidate_processor(torch.randn(2, 6))
    assert processor.alpha == 1.0 and processor.gate is None
    prefix = torch.zeros(2, 1, dtype=torch.long)
    scores = torch.randn(2, 7)
    _, _, expected, _ = processor.distributions(prefix, scores)
    torch.testing.assert_close(processor(prefix, scores)[:, 1:4], expected)


def test_fixed_alpha_one_mixture_matches_catalog_ce_and_total_gradient():
    actual = copmrec("fixed_alpha_one")
    x, y = batch()
    values = actual.losses(x, y.target_ids, training=True)
    hierarchies = actual.num_hierarchies
    torch.testing.assert_close(values["mixture_loss"], values["content_loss"] / hierarchies)
    expected = values["sid_loss"] + (1 + 1 / hierarchies) * values["content_loss"]
    torch.testing.assert_close(values["loss"], expected)
    parameters = [p for p in actual.parameters() if p.requires_grad]
    actual_gradients = torch.autograd.grad(values["loss"], parameters, retain_graph=True)
    expected_gradients = torch.autograd.grad(expected, parameters)
    for actual_gradient, expected_gradient in zip(actual_gradients, expected_gradients, strict=True):
        assert torch.isfinite(actual_gradient).all()
        torch.testing.assert_close(actual_gradient, expected_gradient, atol=2e-6, rtol=2e-5)


def test_fixed_alpha_one_prefix_observations_match_exact_training_mass():
    actual = copmrec("fixed_alpha_one").eval()
    x, y = batch()
    observed = prefix_observations(actual, x, y.target_ids)
    for row in observed:
        torch.testing.assert_close(row["mixed_nll"], row["mass_nll"], rtol=0, atol=0)
        torch.testing.assert_close(row["mixed_probability"], row["mass_probability"], rtol=0, atol=0)
    torch.testing.assert_close(
        torch.stack([row["mixed_nll"] for row in observed]).mean(), actual.losses(x, y.target_ids)["mixture_loss"]
    )


def test_fixed_alpha_one_preserves_full_initialization_and_dropout_rng():
    options = dict(dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(200)
    full = copmrec(**options)
    full_rng = torch.get_rng_state()
    torch.manual_seed(200)
    fixed = copmrec("fixed_alpha_one", **options)
    assert torch.equal(torch.get_rng_state(), full_rng)
    for name, value in full.state_dict().items():
        torch.testing.assert_close(fixed.state_dict()[name], value, rtol=0, atol=0)
    x, y = batch()
    torch.manual_seed(100)
    full_values = full.losses(x, y.target_ids, training=True)
    full_rng = torch.get_rng_state()
    torch.manual_seed(100)
    fixed_values = fixed.losses(x, y.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), full_rng)
    for name in ("sid_loss", "content_loss"):
        torch.testing.assert_close(fixed_values[name], full_values[name], rtol=0, atol=0)


def test_fixed_alpha_one_freezes_zero_gate_and_excludes_it_from_optimizer():
    actual, saved = snapshot("fixed_alpha_one", updates=2)
    assert not actual.dynamic_gate.bias.requires_grad
    assert actual.dynamic_gate.bias.grad is None
    assert torch.count_nonzero(actual.dynamic_gate.bias) == 0
    optimizer = actual.configure_optimizers()["optimizer"]
    assert all(p is not actual.dynamic_gate.bias for group in optimizer.param_groups for p in group["params"])
    assert saved["copmrec_alpha_policy"] == "frozen_1"
    assert saved["copmrec_fixed_mixture_alpha"] == 1.0
    contract = saved["copmrec_unified_scratch"]
    assert contract["alpha_policy"] == "frozen_1"
    assert contract["loss_weights"] == {"sid_ce": 1, "joint_catalog_ce": 1, "mixture_nll": 1}
    assert contract["m3_ablation"]["variant"] == "fixed_alpha_one"


@pytest.mark.parametrize("fault", ["gate", "alpha_policy", "fixed_alpha", "bool_alpha"])
def test_fixed_alpha_one_rejects_wrong_endpoint_identity_or_gate_state(fault):
    _, saved = snapshot("fixed_alpha_one")
    saved = copy.deepcopy(saved)
    if fault == "gate":
        saved["state_dict"]["dynamic_gate.bias"].fill_(0.1)
    elif fault == "alpha_policy":
        saved["copmrec_alpha_policy"] = "learned"
    elif fault == "fixed_alpha":
        saved["copmrec_fixed_mixture_alpha"] = 0.5
    else:
        saved["copmrec_fixed_mixture_alpha"] = True
    with pytest.raises(ValueError):
        copmrec("fixed_alpha_one").on_load_checkpoint(saved)


def test_learned_full_and_existing_ablation_checkpoint_alpha_contract_stays_unchanged():
    for variant in (None, "no_mixture", "no_residual", "no_joint_ce"):
        _, saved = snapshot(variant)
        assert saved["copmrec_alpha_policy"] == "learned"
        assert saved["copmrec_fixed_mixture_alpha"] is None
