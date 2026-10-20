"""用独立手工计算验证 IntRR 递归、STE 以及目标前缀隔离。"""

import pytest
import torch
from torch.nn import functional as F

from src.recommendation.intrr.ran import RecursiveAssignmentNetwork


def small_ran(hierarchies=3, temperature=1.0):
    model = RecursiveAssignmentNetwork(
        num_hierarchies=hierarchies,
        num_embeddings_per_hierarchy=3,
        embedding_dim=2,
        hidden_dim=3,
        temperature=temperature,
    ).double()
    with torch.no_grad():
        for level, codebook in enumerate(model.codebooks):
            codebook.copy_(torch.tensor([[1.0, 0.2], [-0.5, 1.0], [0.1, -0.8]]) + level * 0.15)
        for transition in model.transitions:
            transition[0].weight.copy_(
                torch.tensor([[0.8, -0.3, 0.2, 0.5], [-0.1, 0.7, 0.4, -0.2], [0.3, 0.4, 0.6, 0.1]])
            )
            transition[0].bias.copy_(torch.tensor([0.3, 0.2, 0.1]))
            transition[2].weight.copy_(torch.tensor([[0.5, -0.2, 0.4], [-0.1, 0.8, 0.3]]))
            transition[2].bias.copy_(torch.tensor([0.1, -0.05]))
    return model


def manual_reference(model, guidance, teacher_sids=None):
    """只使用矩阵公式独立构造参考，不调用被测 step/run。"""
    selected = None
    codes, logits = [], []
    for level, codebook in enumerate(model.codebooks):
        if level == 0:
            hidden = guidance
        else:
            previous = selected if teacher_sids is None else model.codebooks[level - 1][teacher_sids[..., level - 1]]
            joined = torch.cat([previous, guidance], dim=-1)
            first, _, second = model.transitions[level - 1]
            hidden = F.linear(F.linear(joined, first.weight, first.bias).relu(), second.weight, second.bias)
        scores = torch.einsum("...d,kd->...k", hidden, codebook)
        hard = codebook[scores.argmax(dim=-1)]
        selected = hard
        codes.append(selected)
        logits.append(scores)
    return torch.stack(codes, -2).sum(-2), torch.stack(logits, -2)


@pytest.mark.parametrize("leading_shape", [(2,), (2, 3)])
@pytest.mark.parametrize("teacher_forcing", [False, True])
def test_matches_independent_recursive_reference(leading_shape, teacher_forcing):
    model = small_ran()
    guidance = torch.linspace(-0.4, 0.9, torch.tensor(leading_shape).prod().item() * 2, dtype=torch.double).reshape(
        *leading_shape, 2
    )
    targets = torch.arange(torch.tensor(leading_shape).prod().item() * 3).reshape(*leading_shape, 3) % 3
    targets = targets if teacher_forcing else None
    actual_embedding, actual_logits = model.run(guidance, targets)
    expected_embedding, expected_logits = manual_reference(model, guidance, targets)
    torch.testing.assert_close(actual_embedding, expected_embedding)
    torch.testing.assert_close(actual_logits, expected_logits)
    assert actual_logits.shape == (*leading_shape, 3, 3)
    assert actual_embedding.shape == (*leading_shape, 2)


def test_ste_hard_forward_and_soft_backward_match_manual_gradient():
    model = small_ran(hierarchies=1, temperature=0.7)
    guidance = torch.tensor([[0.2, 0.5], [-0.1, 0.4]], dtype=torch.double, requires_grad=True)
    codebook = model.codebooks[0]
    scores = guidance @ codebook.T
    hard = codebook[scores.argmax(-1)]
    soft = scores.div(0.7).softmax(-1) @ codebook
    actual, logits = model(guidance)
    torch.testing.assert_close(actual, hard)
    torch.testing.assert_close(logits[:, 0], scores)
    assert not torch.allclose(actual, soft)
    weights = torch.tensor([[0.4, -0.2], [0.8, 0.3]], dtype=torch.double)
    actual_gradients = torch.autograd.grad((actual * weights).sum(), (guidance, codebook), retain_graph=True)
    expected_gradients = torch.autograd.grad((soft * weights).sum(), (guidance, codebook))
    for actual_gradient, expected_gradient in zip(actual_gradients, expected_gradients, strict=True):
        torch.testing.assert_close(actual_gradient, expected_gradient)
        assert torch.isfinite(actual_gradient).all() and actual_gradient.norm() > 0


def test_recursive_ste_reaches_guidance_codebooks_and_transitions():
    model = small_ran()
    guidance = torch.tensor([[0.2, 0.5], [-0.1, 0.4]], dtype=torch.double, requires_grad=True)
    model(guidance)[0].square().sum().backward()
    for gradient in [guidance.grad, *[parameter.grad for parameter in model.parameters()]]:
        assert gradient is not None and torch.isfinite(gradient).all()
        assert gradient.norm() > 0


def test_teacher_forcing_only_reads_previous_target_and_shares_codebooks():
    model = small_ran()
    guidance = torch.tensor([[0.2, 0.5]], dtype=torch.double)
    targets = torch.tensor([[0, 1, 2]])
    _, original = model(guidance, targets)
    changed = targets.clone()
    changed[:, 1:] = torch.tensor([[2, 0]])
    _, future_changed = model(guidance, changed)
    torch.testing.assert_close(original[:, :2], future_changed[:, :2], rtol=0, atol=0)
    assert not torch.allclose(original[:, 2], future_changed[:, 2])
    changed = targets.clone()
    changed[:, 0] = 1
    _, prefix_changed = model(guidance, changed)
    torch.testing.assert_close(original[:, 0], prefix_changed[:, 0], rtol=0, atol=0)
    assert not torch.allclose(original[:, 1], prefix_changed[:, 1])
    _, last_changed = model(guidance, torch.tensor([[0, 1, 0]]))
    torch.testing.assert_close(original, last_changed, rtol=0, atol=0)
    previous_code = model.codebooks[0][targets[:, 0]]
    expected, _ = model.step(guidance, 1, previous_code)
    torch.testing.assert_close(original[:, 1], expected)


def test_temperature_affects_soft_gradient_but_not_logits_or_hard_forward():
    model = small_ran(temperature=0.2)
    guidance = torch.tensor([[0.2, 0.5]], dtype=torch.double, requires_grad=True)
    first_embedding, first_logits = model(guidance)
    first_gradient = torch.autograd.grad(first_embedding.sum(), guidance)[0]
    model.temperature = 2.0
    second_embedding, second_logits = model(guidance)
    second_gradient = torch.autograd.grad(second_embedding.sum(), guidance)[0]
    torch.testing.assert_close(first_embedding, second_embedding)
    torch.testing.assert_close(first_logits, second_logits)
    assert not torch.allclose(first_gradient, second_gradient)


@pytest.mark.parametrize("name", ["num_hierarchies", "num_embeddings_per_hierarchy", "embedding_dim", "hidden_dim"])
@pytest.mark.parametrize("invalid", [0, -1, 1.5, True])
def test_rejects_invalid_dimensions(name, invalid):
    arguments = dict(num_hierarchies=2, num_embeddings_per_hierarchy=3, embedding_dim=2, hidden_dim=3)
    arguments[name] = invalid
    with pytest.raises(ValueError, match=name):
        RecursiveAssignmentNetwork(**arguments)


@pytest.mark.parametrize("temperature", [0, -0.5, float("nan"), float("inf"), True, "1"])
def test_rejects_invalid_temperature(temperature):
    with pytest.raises(ValueError, match="temperature"):
        small_ran(temperature=temperature)


@pytest.mark.parametrize("guidance", [torch.ones(2), torch.ones(2, 4), torch.ones(1, 2, dtype=torch.long)])
def test_rejects_invalid_guidance(guidance):
    with pytest.raises((ValueError, TypeError), match="guidance"):
        small_ran()(guidance)


@pytest.mark.parametrize(
    "targets",
    [
        torch.ones(2, 2),
        torch.ones(2, 3),
        torch.ones(2, 3, dtype=torch.bool),
        torch.zeros(2, 2, dtype=torch.long),
        torch.full((2, 3), -1),
        torch.full((2, 3), 3),
    ],
)
def test_rejects_invalid_teacher_targets(targets):
    with pytest.raises((ValueError, TypeError), match="teacher_sids"):
        small_ran()(torch.ones(2, 2, dtype=torch.double), targets)


@pytest.mark.parametrize("level", [-1, 3, True, 1.5])
def test_rejects_invalid_step_level(level):
    with pytest.raises(ValueError, match="level"):
        small_ran().step(torch.ones(2, 2, dtype=torch.double), level)


def test_rejects_invalid_previous_code():
    model = small_ran()
    guidance = torch.ones(2, 2, dtype=torch.double)
    with pytest.raises(ValueError, match="first hierarchy"):
        model.step(guidance, 0, guidance)
    with pytest.raises(TypeError, match="previous_code"):
        model.step(guidance, 1)
    with pytest.raises(TypeError, match="previous_code"):
        model.step(guidance, 1, torch.ones(2, 2, dtype=torch.long))
    with pytest.raises(ValueError, match="same shape"):
        model.step(guidance, 1, torch.ones(2, 3, dtype=torch.double))
