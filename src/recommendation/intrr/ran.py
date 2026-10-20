"""作者 IntRR 的共享递归分配网络，来源和许可见同目录 SOURCE.md。"""

import math

import torch
from torch import nn
from torch.nn import functional as F


class RecursiveAssignmentNetwork(nn.Module):
    """将指导向量递归分配到 codebook；前向选 hard codeword，梯度经 soft 分配。"""

    def __init__(
        self,
        *,
        num_hierarchies: int,
        num_embeddings_per_hierarchy: int,
        embedding_dim: int,
        hidden_dim: int,
        temperature: float = 1.0,
    ):
        super().__init__()
        for name, value in (
            ("num_hierarchies", num_hierarchies),
            ("num_embeddings_per_hierarchy", num_embeddings_per_hierarchy),
            ("embedding_dim", embedding_dim),
            ("hidden_dim", hidden_dim),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")
        if (
            isinstance(temperature, bool)
            or not isinstance(temperature, (int, float))
            or not math.isfinite(temperature)
            or temperature <= 0
        ):
            raise ValueError("temperature must be finite and positive.")
        self.num_hierarchies = num_hierarchies
        self.num_embeddings_per_hierarchy = num_embeddings_per_hierarchy
        self.embedding_dim = embedding_dim
        self.temperature = float(temperature)
        self.codebooks = nn.ParameterList(
            [nn.Parameter(torch.randn(num_embeddings_per_hierarchy, embedding_dim)) for _ in range(num_hierarchies)]
        )
        self.transitions = nn.ModuleList(
            [
                nn.Sequential(nn.Linear(2 * embedding_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, embedding_dim))
                for _ in range(num_hierarchies - 1)
            ]
        )

    def _validate_guidance(self, guidance: torch.Tensor):
        if not isinstance(guidance, torch.Tensor) or not guidance.is_floating_point():
            raise TypeError("guidance must be a floating-point tensor.")
        if guidance.ndim < 2 or guidance.shape[-1] != self.embedding_dim:
            raise ValueError(f"guidance must have shape [*, {self.embedding_dim}] with at least one batch dimension.")

    def step(
        self,
        guidance: torch.Tensor,
        level: int,
        previous_code: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """返回单层原始 logits 和 STE codeword，形状分别为 [*, K] 与 [*, d]。

        previous_code 为上一层的 codeword 向量；beam 生成时从上一层 codebook
        按实际前缀查表传入。temperature 仅用于 STE，不缩放返回的原始 logits。
        """
        self._validate_guidance(guidance)
        if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level < self.num_hierarchies:
            raise ValueError("level must index an existing hierarchy.")
        if level == 0:
            if previous_code is not None:
                raise ValueError("The first hierarchy does not accept previous_code.")
            hidden = guidance
        else:
            if not isinstance(previous_code, torch.Tensor) or not previous_code.is_floating_point():
                raise TypeError("previous_code must be a floating-point codeword tensor after the first hierarchy.")
            if previous_code.shape != guidance.shape:
                raise ValueError("previous_code must have the same shape as guidance.")
            hidden = self.transitions[level - 1](torch.cat([previous_code, guidance], dim=-1))
        codebook = self.codebooks[level]
        logits = hidden @ codebook.T
        probabilities = F.softmax(logits / self.temperature, dim=-1)
        soft_code = probabilities @ codebook
        hard_code = F.embedding(probabilities.argmax(dim=-1), codebook)
        selected_code = soft_code + (hard_code - soft_code).detach()
        return logits, selected_code

    def run(
        self,
        guidance: torch.Tensor,
        teacher_sids: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """返回各层 STE codeword 之和 [*, d] 与原始 logits [*, H, K]。

        teacher_sids 的形状为 [*, H]；第 h 层只能使用第 h-1 个目标 codeword。
        不提供目标时，递归使用上一层的 STE 分配。
        """
        self._validate_guidance(guidance)
        if teacher_sids is not None:
            if not isinstance(teacher_sids, torch.Tensor) or teacher_sids.dtype not in (
                torch.uint8,
                torch.int8,
                torch.int16,
                torch.int32,
                torch.int64,
            ):
                raise TypeError("teacher_sids must be an integer tensor.")
            if teacher_sids.shape != (*guidance.shape[:-1], self.num_hierarchies):
                raise ValueError("teacher_sids must match guidance batch dimensions and the number of hierarchies.")
            if teacher_sids.device != guidance.device:
                raise ValueError("teacher_sids and guidance must be on the same device.")
            if ((teacher_sids < 0) | (teacher_sids >= self.num_embeddings_per_hierarchy)).any():
                raise ValueError("teacher_sids contain a codebook index outside the valid range.")
        selected = None
        embeddings = []
        logits = []
        for level in range(self.num_hierarchies):
            previous_code = selected
            if level > 0 and teacher_sids is not None:
                previous_code = F.embedding(teacher_sids[..., level - 1].long(), self.codebooks[level - 1])
            level_logits, selected = self.step(guidance, level, previous_code)
            embeddings.append(selected)
            logits.append(level_logits)
        return torch.stack(embeddings, dim=-2).sum(dim=-2), torch.stack(logits, dim=-2)

    def forward(
        self,
        guidance: torch.Tensor,
        teacher_sids: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        return self.run(guidance, teacher_sids)
