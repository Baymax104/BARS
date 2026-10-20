"""验证 IntRR causal backbone 与作者 FF 的真实运算顺序。"""

import pytest
import torch
from torch import nn
from transformers import T5Config

from src.recommendation.intrr.backbone import IntrrBackbone, IntrrFeedForward


def backbone():
    torch.manual_seed(7)
    return IntrrBackbone(embedding_dim=8, num_layers=2, num_heads=2, d_kv=4, feedforward_dim=16, dropout=0)


def test_causal_states_do_not_read_future_items_or_padding():
    model = backbone().eval()
    embeddings = torch.randn(2, 4, 8)
    mask = torch.tensor([[1, 1, 1, 1], [1, 1, 0, 0]])
    original = model(embeddings, mask)
    changed = embeddings.clone()
    changed[:, 2:] += torch.randn(2, 2, 8) * 20
    modified = model(changed, mask)
    torch.testing.assert_close(original[:, :2], modified[:, :2], rtol=0, atol=0)
    assert not torch.allclose(original[0, 2:], modified[0, 2:])


def test_feedforward_matches_author_layer_order_and_has_no_final_relu():
    config = T5Config(d_model=4, d_ff=6, dropout_rate=0)
    layer = IntrrFeedForward(config)
    assert [type(module) for module in layer.mlp] == [
        nn.Linear,
        nn.ReLU,
        nn.Linear,
        nn.Dropout,
        nn.ReLU,
        nn.Linear,
        nn.Dropout,
    ]
    hidden = torch.randn(2, 3, 4)
    normalized = (
        hidden
        * torch.rsqrt(hidden.square().mean(-1, keepdim=True) + config.layer_norm_epsilon)
        * layer.layer_norm.weight
    )
    first, _, second, _, _, third, _ = layer.mlp
    expected = torch.nn.functional.linear(normalized, first.weight, first.bias).relu()
    expected = torch.nn.functional.linear(expected, second.weight, second.bias).relu()
    expected = torch.nn.functional.linear(expected, third.weight, third.bias)
    torch.testing.assert_close(layer(hidden), hidden + expected)
    with torch.no_grad():
        third.weight.zero_()
        third.bias.fill_(-1)
    torch.testing.assert_close(layer(torch.zeros(1, 1, 4)), -torch.ones(1, 1, 4))


def test_only_unused_cross_attention_is_frozen_and_all_live_parameters_receive_gradients():
    model = backbone()
    hidden = model(torch.randn(2, 3, 8), torch.ones(2, 3))
    hidden.square().mean().backward()
    for name, parameter in model.named_parameters():
        if ".layer.1." in name:
            assert not parameter.requires_grad and parameter.grad is None
        else:
            assert parameter.requires_grad and parameter.grad is not None
            assert torch.isfinite(parameter.grad).all()
    assert model.transformer.embed_tokens is None


@pytest.mark.parametrize(
    "arguments", [{"num_layers": 0}, {"num_heads": True}, {"dropout": 1}, {"feedforward_hidden_layers": 0}]
)
def test_rejects_invalid_backbone_configuration(arguments):
    with pytest.raises(ValueError):
        IntrrBackbone(**arguments)
