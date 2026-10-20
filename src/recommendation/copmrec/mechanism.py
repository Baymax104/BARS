"""固定 Untied checkpoint 的生成／排序 2×2 干预；不改变正式部署。"""

import hashlib
import re
from collections import defaultdict

import numpy as np
import torch
from lightning import LightningModule
from omegaconf import OmegaConf
from transformers.modeling_outputs import BaseModelOutput

from src.common.writers.structured_analysis import StructuredAnalysisOutput
from src.data.components.data_models import ModelOutput
from src.data.utils import gather_predictions_by_keys
from src.recommendation.copmrec.diagnosis import retrieval_values
from src.recommendation.liger.candidate_guidance import ProbabilityMixtureProcessor

MECHANISM_PROTOCOL = "bars-untied-mechanism-beauty42-20261019-v1"
GENERATORS = ("learned", "alpha0")
RANKERS = ("catalog", "decoder")
ARMS = tuple(f"{generation}_{ranking}" for generation in GENERATORS for ranking in RANKERS)
METRICS = ("recall@5", "ndcg@5", "recall@10", "ndcg@10")


@torch.no_grad()
def candidate_decoder_scores(model, encoded, mask, users, rows, *, batch_size):
    """所有候选（含 cold）使用完整 encoder states 和同一合法支持计算路径概率。"""
    result = encoded.last_hidden_state.new_empty(len(rows), dtype=torch.float32)
    # 合法支持只依赖固定 SID 树；单个伪用户避免复制 batch×目录 posterior。
    processor = ProbabilityMixtureProcessor(
        model.semantic_ids,
        result.new_zeros(1, len(model.semantic_ids)),
        model.codebook_size,
        0.0,
    )
    for start in range(0, len(rows), batch_size):
        selected = slice(start, start + batch_size)
        user = users[selected]
        local = model.semantic_ids[rows[selected]]
        tokens = local + model.offsets
        candidate_encoded = BaseModelOutput(last_hidden_state=encoded.last_hidden_state.index_select(0, user))
        decoded = model.transformer(
            encoder_outputs=candidate_encoded,
            attention_mask=mask.index_select(0, user),
            labels=tokens,
            use_cache=False,
        )
        prefix = tokens.new_full((len(tokens), 1), model.transformer.config.decoder_start_token_id)
        score = result.new_zeros(len(tokens))
        for depth in range(model.num_hierarchies):
            _, generation, _, valid = processor.distributions(prefix, decoded.logits[:, depth].float())
            target = local[:, depth, None]
            if not valid.gather(1, target).all():
                raise ValueError("Candidate path is absent from the legal SID tree.")
            score += generation.gather(1, target).squeeze(1)
            prefix = torch.cat((prefix, tokens[:, depth, None]), dim=1)
        if not torch.isfinite(score).all():
            raise ValueError("Every candidate, including cold items, requires a finite decoder path score.")
        result[selected] = score
    return result


class CoPMRecMechanismDiagnosis(LightningModule):
    def __init__(
        self,
        *,
        backbone,
        checkpoint,
        reference_predictions,
        source_reference,
        source_sha256,
        prediction_reference=None,
        input_references=None,
        bootstrap_repetitions=2000,
        generation_candidates=20,
        top_k=10,
        candidate_score_batch_size=64,
        num_hierarchies=None,
    ):
        super().__init__()
        if getattr(backbone, "variant", None) != "untied_residual":
            raise ValueError("Mechanism diagnosis requires the current Untied Full backbone.")
        if num_hierarchies is not None and num_hierarchies != backbone.num_hierarchies:
            raise ValueError("Mechanism preprocessing and backbone SID depths differ.")
        input_references = (
            OmegaConf.to_container(input_references, resolve=True)
            if OmegaConf.is_config(input_references)
            else input_references
        )
        if input_references is not None and (
            input_references.get("dataset", "beauty") != "beauty" or input_references.get("training_seed", 42) != 42
        ):
            raise ValueError("The current mechanism stage is restricted to Beauty/seed42.")
        for name, value in (
            ("bootstrap repetitions", bootstrap_repetitions),
            ("generation candidates", generation_candidates),
            ("top k", top_k),
            ("candidate score batch size", candidate_score_batch_size),
        ):
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        if backbone.generation_candidates != generation_candidates or backbone.top_k != top_k:
            raise ValueError("Mechanism candidate budget and TopK must match the frozen production deployment.")
        if (
            not source_reference
            or not isinstance(source_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", source_sha256) is None
        ):
            raise ValueError("Mechanism source requires an explicit reference and audited SHA256.")
        if checkpoint is None:
            raise ValueError("Mechanism diagnosis requires the audited Untied own-best checkpoint.")
        backbone.on_load_checkpoint(checkpoint)
        backbone.load_state_dict(checkpoint["state_dict"], strict=True)
        self.backbone = backbone.eval().requires_grad_(False)
        deployment = reference_predictions.auxiliary.get("deployment_contract")
        if (
            backbone.prediction_mode != "hybrid"
            or not isinstance(deployment, dict)
            or deployment != backbone.deployment_contract
        ):
            raise ValueError("Reference must carry the verified current Untied hybrid deployment contract.")
        reference_keys = reference_predictions.keys
        if reference_keys.ndim != 1 or reference_keys.dtype not in (torch.int32, torch.int64):
            raise ValueError("Reference requires one-dimensional integer business user keys.")
        if len(reference_keys.unique()) != len(reference_keys):
            raise ValueError("Reference contains duplicate user keys.")
        if not len(reference_keys):
            raise ValueError("Reference requires at least one measured user.")
        if reference_predictions.predictions.shape != (len(reference_keys), top_k, backbone.num_hierarchies):
            raise ValueError("Reference requires complete production TopK SIDs.")
        reference_rows = backbone.lookup_rows(reference_predictions.predictions.to(backbone.semantic_ids.device))
        if any(len(row.unique()) != top_k for row in reference_rows):
            raise ValueError("Reference TopK contains duplicate items.")
        order = reference_keys.argsort(stable=True)
        self.reference_predictions = ModelOutput(
            keys=reference_keys[order].cpu(),
            predictions=reference_predictions.predictions[order].cpu(),
            auxiliary=dict(reference_predictions.auxiliary),
        )
        self.top_k = top_k
        self.generation_candidates = generation_candidates
        self.candidate_score_batch_size = candidate_score_batch_size
        self.bootstrap_repetitions = bootstrap_repetitions
        self.rows, self.keys, self.predictions = [], [], defaultdict(list)
        self.metadata = dict(
            protocol=MECHANISM_PROTOCOL,
            evidence_kind="fixed_checkpoint_intervention",
            training_updates=0,
            scope="single_dataset_single_seed",
            training_seed=backbone.initialization_seed,
            source_variant="untied_residual",
            source_reference=source_reference,
            source_sha256=source_sha256,
            prediction_reference=prediction_reference,
            prediction_sha256=reference_predictions.auxiliary.get("source_sha256"),
            input_references=input_references,
            catalog_sha256=backbone.catalog_sha256,
            generation_conditions=list(GENERATORS),
            ranking_conditions=list(RANKERS),
            generation_candidates=generation_candidates,
            top_k=top_k,
            candidate_score_batch_size=candidate_score_batch_size,
            candidate_pool="beam_plus_all_cold",
            decoder_score="sum_of_legal_conditional_decoder_log_probabilities_over_complete_sid",
            decoder_context="full_encoder_states",
            history_exclusion=False,
            rank_ties="stable_catalog_row",
            reference_arm="learned_catalog",
            source_deployment_contract=backbone.deployment_contract,
            learned_alpha=float(backbone.effective_mixture_alpha()),
            bootstrap=dict(rng="PCG64", seed=42, repetitions=bootstrap_repetitions, confidence=0.95, pointwise=True),
        )

    def on_test_start(self):
        if self.trainer.world_size != 1:
            raise ValueError("Mechanism diagnosis requires a single process.")
        self.backbone.eval()
        self.rows.clear()
        self.keys.clear()
        self.predictions.clear()

    @torch.no_grad()
    def test_step(self, batch, batch_idx):
        x, label = batch
        if label is None or x.output_keys is None:
            raise ValueError("Mechanism measurement requires labels and business user keys.")
        model = self.backbone
        keys = x.output_keys.reshape(-1)
        labels = label.target_ids
        if len(keys) != len(labels) or keys.dtype not in (torch.int32, torch.int64):
            raise ValueError("Mechanism user keys and labels must align.")
        targets = model.lookup_rows(labels)
        reference = gather_predictions_by_keys(self.reference_predictions, keys.cpu()).to(labels.device)
        encoded, mask, query = model.encode(x.input_ids, x.attention_mask)
        logits = model.dense_logits(query)
        if not torch.isfinite(logits).all():
            raise ValueError("Mechanism requires finite full-catalog logits.")
        generated = {
            name: model._generate_candidate_rows(
                encoded,
                mask,
                processor=(
                    model.candidate_processor(logits)
                    if name == "learned"
                    else ProbabilityMixtureProcessor(model.semantic_ids, logits, model.codebook_size, 0.0)
                ),
                generation_candidates=self.generation_candidates,
            )
            for name in GENERATORS
        }
        cold = (~model.seen_mask).nonzero().flatten()
        pools, unions = {}, []
        for user in range(len(keys)):
            for name in GENERATORS:
                beam = generated[name][user]
                if ((beam < -1) | (beam >= len(model.item_keys))).any():
                    raise ValueError("Generated catalog row is invalid.")
                pools[name, user] = torch.cat((beam[beam >= 0], cold)).unique(sorted=True)
                if len(pools[name, user]) < self.top_k:
                    raise ValueError("Candidate union cannot supply a legal unique TopK.")
            unions.append(torch.cat([pools[name, user] for name in GENERATORS]).unique(sorted=True))
        users = torch.cat([torch.full_like(rows, user) for user, rows in enumerate(unions)])
        all_rows = torch.cat(unions)
        decoder_scores = candidate_decoder_scores(
            model, encoded, mask, users, all_rows, batch_size=self.candidate_score_batch_size
        ).split([len(rows) for rows in unions])
        dense_order = logits.argsort(dim=-1, descending=True, stable=True)
        predictions, records = {}, []
        for name in GENERATORS:
            for ranker in RANKERS:
                arm = f"{name}_{ranker}"
                arm_predictions = []
                for user in range(len(keys)):
                    pool = pools[name, user]
                    scores = (
                        logits[user, pool]
                        if ranker == "catalog"
                        else decoder_scores[user][torch.searchsorted(unions[user], pool)]
                    )
                    ordered = pool[scores.argsort(descending=True, stable=True)]
                    arm_predictions.append(model.semantic_ids[ordered[: self.top_k]])
                    target = targets[user]
                    found = (ordered == target).nonzero().flatten()
                    records.append(
                        dict(
                            user_key=int(keys[user]),
                            variant=arm,
                            generation=name,
                            ranking=ranker,
                            target_row=int(target),
                            target_seen=bool(model.seen_mask[target]),
                            target_generated=bool((generated[name][user] == target).any()),
                            target_covered=bool(len(found)),
                            candidate_count=len(pool),
                            generated_unique_count=int(
                                generated[name][user][generated[name][user] >= 0].unique().numel()
                            ),
                            invalid_generated_count=int((generated[name][user] < 0).sum()),
                            target_rank=int(found[0]) + 1 if len(found) else 0,
                            dense_rank=int((dense_order[user] == target).nonzero()[0, 0]) + 1,
                        )
                    )
                predictions[arm] = torch.stack(arm_predictions)
        if not torch.equal(predictions["learned_catalog"], reference):
            raise ValueError("Learned-catalog arm does not exactly reproduce the frozen production TopK.")
        values = {arm: retrieval_values(predictions[arm], labels) for arm in ARMS}
        for row in records:
            user = (keys == row["user_key"]).nonzero()[0, 0]
            row.update({metric: float(values[row["variant"]][metric][user]) for metric in METRICS})
            if (row["recall@10"] > 0 and not row["target_covered"]) or (
                row["target_generated"] and not row["target_covered"]
            ):
                raise ValueError("Candidate coverage and final hit containment is inconsistent.")
        dense_predictions = model.semantic_ids[dense_order[:, : self.top_k]]
        dense_values = retrieval_values(dense_predictions, labels)
        for user, key in enumerate(keys):
            records.append(
                dict(
                    user_key=int(key),
                    variant="dense_catalog",
                    target_row=int(targets[user]),
                    **{metric: float(dense_values[metric][user]) for metric in METRICS},
                )
            )
        self.rows.extend(records)
        self.keys.append(keys.cpu())
        for arm, prediction in {**predictions, "dense_catalog": dense_predictions}.items():
            self.predictions[arm].append(prediction.cpu())
        return {}

    def structured_analysis_output(self):
        if not self.keys:
            raise ValueError("Mechanism analysis has no measured users.")
        keys = torch.cat(self.keys)
        if len(keys.unique()) != len(keys):
            raise ValueError("Mechanism analysis contains duplicate user keys.")
        if set(keys.tolist()) != set(self.reference_predictions.keys.tolist()):
            raise ValueError("Mechanism and frozen reference user populations differ.")
        by_arm = {arm: {} for arm in (*ARMS, "dense_catalog")}
        for row in self.rows:
            by_arm[row["variant"]][row["user_key"]] = row
        ordered_keys = sorted(keys.tolist())
        values = np.array(
            [[[by_arm[arm][key][metric] for metric in METRICS] for arm in ARMS] for key in ordered_keys],
            dtype=np.float64,
        )
        rng = np.random.Generator(np.random.PCG64(42))
        bootstrap = np.array(
            [values[rng.integers(len(values), size=len(values))].mean(0) for _ in range(self.bootstrap_repetitions)]
        )
        comparisons, cases = [], []
        pairs = (
            ("generation_at_catalog", "learned_catalog", "alpha0_catalog"),
            ("generation_at_decoder", "learned_decoder", "alpha0_decoder"),
            ("ranking_at_learned", "learned_catalog", "learned_decoder"),
            ("ranking_at_alpha0", "alpha0_catalog", "alpha0_decoder"),
            ("both_at_production", "learned_catalog", "alpha0_decoder"),
        )
        for name, left, right in pairs:
            li, ri = ARMS.index(left), ARMS.index(right)
            delta = values[:, li] - values[:, ri]
            interval = np.quantile(bootstrap[:, li] - bootstrap[:, ri], [0.025, 0.975], axis=0)
            for metric_index, metric in enumerate(METRICS):
                comparisons.append(
                    dict(
                        comparison=name,
                        left=left,
                        right=right,
                        direction="left_minus_right",
                        metric=metric,
                        n=len(keys),
                        difference=float(delta[:, metric_index].mean()),
                        reference_mean=float(values[:, ri, metric_index].mean()),
                        ci_low=float(interval[0, metric_index]),
                        ci_high=float(interval[1, metric_index]),
                    )
                )
            for k in (5, 10):
                hit_index, ndcg_index = METRICS.index(f"recall@{k}"), METRICS.index(f"ndcg@{k}")
                lh, rh = values[:, li, hit_index].astype(bool), values[:, ri, hit_index].astype(bool)
                groups = {"left_only": lh & ~rh, "right_only": rh & ~lh, "both": lh & rh, "neither": ~lh & ~rh}
                contribution_sum = 0.0
                for category, selected in groups.items():
                    contribution = float((delta[:, ndcg_index] * selected).mean())
                    contribution_sum += contribution
                    comparisons.append(
                        dict(
                            comparison=name,
                            left=left,
                            right=right,
                            metric=f"ndcg@{k}",
                            category=category,
                            count=int(selected.sum()),
                            fraction=float(selected.mean()),
                            contribution=contribution,
                        )
                    )
                    selected_keys = [key for key, include in zip(ordered_keys, selected, strict=True) if include]
                    selected_keys.sort(key=lambda key: hashlib.sha256(str(key).encode()).hexdigest())
                    cases.extend(
                        dict(
                            comparison=name,
                            category=category,
                            k=k,
                            user_key=key,
                            left_rank=by_arm[left][key]["target_rank"],
                            right_rank=by_arm[right][key]["target_rank"],
                        )
                        for key in selected_keys[:3]
                    )
                if not np.isclose(contribution_sum, delta[:, ndcg_index].mean(), atol=1e-12):
                    raise ValueError("Hit and rank contributions do not sum to the measured NDCG difference.")
        interaction = values[:, 0] - values[:, 2] - values[:, 1] + values[:, 3]
        interaction_samples = bootstrap[:, 0] - bootstrap[:, 2] - bootstrap[:, 1] + bootstrap[:, 3]
        intervals = np.quantile(interaction_samples, [0.025, 0.975], axis=0)
        for index, metric in enumerate(METRICS):
            comparisons.append(
                dict(
                    comparison="generation_ranking_interaction",
                    direction="(learned_catalog-alpha0_catalog)-(learned_decoder-alpha0_decoder)",
                    metric=metric,
                    n=len(keys),
                    difference=float(interaction[:, index].mean()),
                    ci_low=float(intervals[0, index]),
                    ci_high=float(intervals[1, index]),
                )
            )
        observations = []
        for arm, records in by_arm.items():
            observation = dict(variant=arm, n=len(records))
            for field in (
                *METRICS,
                "target_generated",
                "target_covered",
                "candidate_count",
                "generated_unique_count",
                "invalid_generated_count",
                "dense_rank",
            ):
                selected = [row[field] for row in records.values() if field in row]
                if selected:
                    observation[field + "_mean"] = float(np.mean(selected))
            observations.append(observation)
        metadata = {**self.metadata, "user_count": len(keys), "production_reproduced": True}
        return StructuredAnalysisOutput(
            documents={"summary.json": dict(metadata=metadata, observations=observations, comparisons=comparisons)},
            tables={"users.csv": self.rows, "comparisons.csv": comparisons, "cases.csv": cases},
            bundles={
                f"{arm}.pt": dict(keys=keys, predictions=torch.cat(predictions))
                for arm, predictions in self.predictions.items()
            },
            metadata=metadata,
        )
