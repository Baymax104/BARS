"""IntRR 作者实现使用的 causal T5 与多层前馈网络。"""

import torch
from torch import nn
from transformers import T5Config
from transformers.models.t5.modeling_t5 import T5LayerNorm, T5Stack

from src.utils.model import reset_parameters


class IntrrFeedForward(nn.Module):
    """保留作者 MLP 的激活/dropout 顺序及外层 pre-norm 残差。"""

    def __init__(self, config: T5Config, hidden_layers: int = 2):
        super().__init__()
        dimensions = [config.d_model, *[config.d_ff] * hidden_layers, config.d_model]
        layers = [nn.Linear(dimensions[0], dimensions[1])]
        for index in range(1, len(dimensions) - 1):
            layers.extend(
                [nn.ReLU(), nn.Linear(dimensions[index], dimensions[index + 1]), nn.Dropout(config.dropout_rate)]
            )
        self.mlp = nn.Sequential(*layers)
        self.layer_norm = T5LayerNorm(config.d_model, eps=config.layer_norm_epsilon)
        self.dropout = nn.Dropout(config.dropout_rate)

    def forward(self, hidden_states):
        return hidden_states + self.dropout(self.mlp(self.layer_norm(hidden_states)))


class IntrrBackbone(nn.Module):
    """一商品一 token 的 causal T5Stack，无额外 BOS、位置表或 encoder。"""

    def __init__(
        self,
        *,
        embedding_dim=256,
        num_layers=4,
        num_heads=6,
        d_kv=64,
        feedforward_dim=1024,
        feedforward_hidden_layers=2,
        dropout=0.15,
    ):
        super().__init__()
        for name, value in (
            ("embedding_dim", embedding_dim),
            ("num_layers", num_layers),
            ("num_heads", num_heads),
            ("d_kv", d_kv),
            ("feedforward_dim", feedforward_dim),
            ("feedforward_hidden_layers", feedforward_hidden_layers),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        if isinstance(dropout, bool) or not isinstance(dropout, (float, int)) or not 0 <= dropout < 1:
            raise ValueError("dropout must be finite and in [0, 1).")
        config = T5Config(
            vocab_size=1,
            eos_token_id=None,
            d_model=embedding_dim,
            num_layers=num_layers,
            num_heads=num_heads,
            d_kv=d_kv,
            d_ff=feedforward_dim,
            dropout_rate=dropout,
            is_decoder=True,
            is_encoder_decoder=False,
            use_cache=False,
        )
        self.transformer = T5Stack(config)
        self.transformer.embed_tokens = None
        # 作者先以普通 Linear.reset_parameters 重置，再替换 FF。
        reset_parameters(self.transformer)
        for block in self.transformer.block:
            block.layer[-1] = IntrrFeedForward(config, feedforward_hidden_layers)
            # 没有 encoder states，cross-attention 永远不调用。
            block.layer[1].requires_grad_(False)

    def forward(self, embeddings: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        if embeddings.ndim != 3 or attention_mask.shape != embeddings.shape[:2]:
            raise ValueError("embeddings and attention_mask must have shapes [B, S, d] and [B, S].")
        return self.transformer(
            inputs_embeds=embeddings, attention_mask=attention_mask, use_cache=False
        ).last_hidden_state
