"""在 TIGER 数据和评价协议下接入 IntRR 的原生推荐机制。"""

import math

import torch
from lightning import LightningModule
from torch import nn
from torch.nn import functional as F

from src.common.configs.model import TrainingModelConfig
from src.data.components.data_models import ModelOutput, TigerModelInput
from src.recommendation.intrr.backbone import IntrrBackbone
from src.recommendation.intrr.ran import RecursiveAssignmentNetwork


class IntrrRecommender(LightningModule):
    def __init__(
        self,
        *,
        catalog,
        sequence_length=180,
        num_hierarchies=None,
        codebook_size=None,
        training_model_config: TrainingModelConfig | None = None,
        embedding_dim=256,
        item_embedding_dim=512,
        ran_hidden_dim=512,
        num_layers=4,
        num_heads=6,
        d_kv=64,
        feedforward_dim=1024,
        feedforward_hidden_layers=2,
        dropout=0.15,
        temperature=1.0,
        alignment_weight=0.1,
        top_k_for_generation=10,
        should_check_prefix=True,
    ):
        super().__init__()
        if num_hierarchies is not None and num_hierarchies != catalog.num_hierarchies:
            raise ValueError("num_hierarchies must match the catalog.")
        if codebook_size is not None and codebook_size != catalog.codebook_size:
            raise ValueError("codebook_size must match the catalog.")
        self.num_hierarchies = catalog.num_hierarchies
        self.codebook_size = catalog.codebook_size
        for name, value in (
            ("sequence_length", sequence_length),
            ("item_embedding_dim", item_embedding_dim),
            ("top_k_for_generation", top_k_for_generation),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")
        if sequence_length % self.num_hierarchies or sequence_length // self.num_hierarchies < 2:
            raise ValueError("sequence_length must reserve one history item and one target SID.")
        if (
            isinstance(alignment_weight, bool)
            or not isinstance(alignment_weight, (int, float))
            or not math.isfinite(alignment_weight)
            or alignment_weight < 0
        ):
            raise ValueError("alignment_weight must be finite and nonnegative.")
        if should_check_prefix is not True:
            raise ValueError("IntRR requires catalog-valid prefix constraints.")
        if self.codebook_size**self.num_hierarchies - 1 > torch.iinfo(torch.int64).max:
            raise ValueError("SID prefix encoding exceeds the int64 range.")
        self.training_config = training_model_config or TrainingModelConfig()
        self.sequence_length = sequence_length
        self.max_history = sequence_length // self.num_hierarchies - 1
        self.alignment_weight = float(alignment_weight)
        self.top_k_for_generation = top_k_for_generation
        self.register_buffer("item_keys", catalog.keys.long().clone(), persistent=False)
        self.register_buffer("semantic_ids", catalog.semantic_ids.long().clone(), persistent=False)
        self.item_embedding = nn.Embedding(len(catalog.keys), item_embedding_dim)
        self.input_mlp = nn.Linear(item_embedding_dim, embedding_dim)
        self.ran = RecursiveAssignmentNetwork(
            num_hierarchies=self.num_hierarchies,
            num_embeddings_per_hierarchy=self.codebook_size,
            embedding_dim=embedding_dim,
            hidden_dim=ran_hidden_dim,
            temperature=temperature,
        )
        self.backbone = IntrrBackbone(
            embedding_dim=embedding_dim,
            num_layers=num_layers,
            num_heads=num_heads,
            d_kv=d_kv,
            feedforward_dim=feedforward_dim,
            feedforward_hidden_layers=feedforward_hidden_layers,
            dropout=dropout,
        )
        self._prefix_counts = []
        encoded = torch.zeros(len(catalog.keys), dtype=torch.long)
        for level in range(self.num_hierarchies):
            encoded = encoded * self.codebook_size + catalog.semantic_ids[:, level].long()
            keys = torch.unique(encoded, sorted=True)
            self.register_buffer(f"prefix_keys_{level}", keys, persistent=False)
            self._prefix_counts.append(len(keys))
        self.checkpoint_contract = dict(
            protocol="intrr-shared-ran-tiger-v1",
            source_commit="806e0f1969ed61a0748902649b335c0ea066de00",
            catalog_sha256=catalog.sha256,
            num_hierarchies=self.num_hierarchies,
            codebook_size=self.codebook_size,
            sequence_length=sequence_length,
            embedding_dim=embedding_dim,
            item_embedding_dim=item_embedding_dim,
            ran_hidden_dim=ran_hidden_dim,
            num_layers=num_layers,
            num_heads=num_heads,
            d_kv=d_kv,
            feedforward_dim=feedforward_dim,
            feedforward_hidden_layers=feedforward_hidden_layers,
            dropout=dropout,
            temperature=temperature,
            alignment_weight=alignment_weight,
            top_k_for_generation=top_k_for_generation,
        )

    def encode_history(self, model_input):
        ids, mask = model_input.input_ids, model_input.attention_mask.bool()
        if ids.ndim != 2 or ids.shape != mask.shape or ids.shape[1] > self.max_history:
            raise ValueError("IntRR input_ids and attention_mask must be matching [B, S] within max_history.")
        if ids.is_floating_point() or ids.dtype == torch.bool:
            raise TypeError("IntRR input_ids must contain integer compact UIDs.")
        lengths = mask.sum(1)
        if (lengths == 0).any() or not torch.equal(
            mask, torch.arange(ids.shape[1], device=ids.device)[None] < lengths[:, None]
        ):
            raise ValueError("IntRR histories must be nonempty and right-padded.")
        if (ids[~mask] != -1).any() or ((ids[mask] < 0) | (ids[mask] >= len(self.item_keys))).any():
            raise ValueError("IntRR UIDs are outside the catalog or padding is not -1.")
        unique_ids, inverse = torch.unique(ids[mask].long(), sorted=True, return_inverse=True)
        guidance = self.input_mlp(self.item_embedding(unique_ids))
        unique_embeddings, item_logits = self.ran(guidance)
        embeddings = unique_embeddings.new_zeros((*ids.shape, unique_embeddings.shape[-1]))
        embeddings[mask] = unique_embeddings[inverse]
        hidden = self.backbone(embeddings, mask)
        user_state = hidden[torch.arange(len(ids), device=ids.device), lengths - 1]
        logits_at_positions = item_logits[inverse]
        targets_at_positions = self.semantic_ids[unique_ids][inverse]
        alignment_loss = (
            F.cross_entropy(
                logits_at_positions.reshape(-1, self.codebook_size), targets_at_positions.reshape(-1), reduction="none"
            )
            .reshape(-1, self.num_hierarchies)
            .sum(-1)
            .mean()
        )
        return user_state, alignment_loss

    def losses(self, model_input, target_ids):
        user_state, alignment_loss = self.encode_history(model_input)
        return self._losses_from_state(user_state, alignment_loss, target_ids)

    def _losses_from_state(self, user_state, alignment_loss, target_ids):
        _, logits = self.ran(user_state, target_ids)
        sid_loss = (
            F.cross_entropy(logits.reshape(-1, self.codebook_size), target_ids.long().reshape(-1))
            * self.num_hierarchies
        )
        return dict(
            loss=sid_loss + self.alignment_weight * alignment_loss, sid_loss=sid_loss, alignment_loss=alignment_loss
        )

    def forward(self, model_input, target_ids):
        user_state, _ = self.encode_history(model_input)
        return self.ran(user_state, target_ids)[1]

    def _legal_children(self, parent_codes, level):
        candidates = parent_codes[..., None] * self.codebook_size + torch.arange(
            self.codebook_size, device=parent_codes.device
        )
        keys = getattr(self, f"prefix_keys_{level}")
        positions = torch.searchsorted(keys, candidates)
        valid = (positions < len(keys)) & (keys[positions.clamp_max(len(keys) - 1)] == candidates)
        return candidates, valid

    def generate(self, model_input):
        user_state, _ = self.encode_history(model_input)
        return self._generate_from_state(user_state)

    def _generate_from_state(self, user_state):
        batch_size = len(user_state)
        prefixes = torch.empty(batch_size, 1, 0, dtype=torch.long, device=user_state.device)
        parent_codes = torch.zeros(batch_size, 1, dtype=torch.long, device=user_state.device)
        scores = user_state.new_zeros(batch_size, 1)
        for level in range(self.num_hierarchies):
            guidance = user_state[:, None].expand(-1, prefixes.shape[1], -1)
            previous = None if level == 0 else F.embedding(prefixes[..., -1], self.ran.codebooks[level - 1])
            logits, _ = self.ran.step(guidance, level, previous)
            candidate_codes, valid = self._legal_children(parent_codes, level)
            masked_logits = logits.masked_fill(~valid, -torch.inf)
            live = valid.any(-1)
            safe_logits = torch.where(live[..., None], masked_logits, torch.zeros_like(masked_logits))
            log_probabilities = F.log_softmax(safe_logits, -1).masked_fill(~valid, -torch.inf)
            candidates = scores[..., None] + log_probabilities
            width = min(self.top_k_for_generation, self._prefix_counts[level])
            scores, winners = candidates.flatten(1).topk(width, dim=-1, sorted=True)
            parents, tokens = winners // self.codebook_size, winners % self.codebook_size
            prefixes = torch.cat([prefixes.gather(1, parents[..., None].expand(-1, -1, level)), tokens[..., None]], -1)
            parent_codes = candidate_codes.flatten(1).gather(1, winners)
        return prefixes, scores

    def training_step(self, batch, batch_idx):
        model_input, label_data = batch
        if label_data is None:
            raise ValueError("IntRR training requires target SID labels.")
        return self.losses(model_input, label_data.target_ids)

    def eval_step(self, batch):
        model_input, label_data = batch
        user_state, alignment_loss = self.encode_history(model_input)
        result = self._losses_from_state(user_state, alignment_loss, label_data.target_ids)
        generated_ids, marginal_probs = self._generate_from_state(user_state)
        return {
            **result,
            "generated_ids": generated_ids,
            "marginal_probs": marginal_probs,
            "labels": label_data.target_ids,
        }

    def validation_step(self, batch, batch_idx):
        return self.eval_step(batch)

    def test_step(self, batch, batch_idx):
        return self.eval_step(batch)

    def predict_step(self, batch):
        model_input = batch if isinstance(batch, TigerModelInput) else batch[0]
        if model_input.output_keys is None:
            raise ValueError("IntRR prediction requires output_keys.")
        generated_ids, _ = self.generate(model_input)
        return ModelOutput(keys=model_input.output_keys.detach().cpu(), predictions=generated_ids.detach().cpu())

    def configure_optimizers(self):
        if self.training_config.optimizer is None:
            raise ValueError("optimizer is required for IntRR training.")
        optimizer = self.training_config.optimizer(
            params=(parameter for parameter in self.parameters() if parameter.requires_grad)
        )
        if self.training_config.scheduler is None:
            return {"optimizer": optimizer}
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": self.training_config.scheduler(optimizer=optimizer),
                "interval": "step",
                "frequency": 1,
            },
        }

    def on_save_checkpoint(self, checkpoint):
        checkpoint["intrr_contract"] = dict(self.checkpoint_contract)

    def on_load_checkpoint(self, checkpoint):
        if checkpoint.get("intrr_contract") != self.checkpoint_contract:
            raise ValueError("IntRR checkpoint identity does not match the catalog or model configuration.")
