"""CoPMRec v2：联合视图训练、显式验证选点与hybrid推荐。"""

import torch

from src.recommendation.copmrec.catalog import FullCatalogObjective
from src.recommendation.liger.module import Liger


class CoPMRec(FullCatalogObjective):
    copmrec_version = "v2"

    @property
    def formal_release(self):
        return dict(
            protocol="copmrec-formal-joint-only-v2-v1",
            implementation_version=self.copmrec_version,
            evidence_phase="formal",
            initialization_seed=self.initialization_seed,
            native_view_ce=False,
            training_history_exclusion=False,
            validation_history_exclusion=False,
            inference_history_exclusion=False,
            development_checkpoints_eligible=False,
        )

    @property
    def unified_scratch_contract(self):
        # 旧dense来源保持原值；新hybrid训练同时登记一致的候选部署。
        return {
            **super().unified_scratch_contract,
            "deployment": (
                "hybrid_beam_plus_all_cold_without_history_exclusion"
                if self.validation_selection_mode == "hybrid"
                else "raw_full_catalog_dense_without_history_exclusion"
            ),
        }

    @property
    def deployment_contract(self):
        alpha_policy = getattr(self, "ablation_contract", {}).get("alpha_policy", self.mixture_alpha_policy)
        fixed_alpha = 0.5 if alpha_policy == "frozen_0.5" else self.fixed_mixture_alpha_value
        return dict(
            protocol="copmrec-hybrid-deployment-v1",
            mode=self.prediction_mode,
            generation_candidates=self.generation_candidates,
            candidate_strategy=self.candidate_strategy,
            candidate_pool="beam_plus_all_cold" if self.prediction_mode == "hybrid" else "all_catalog",
            final_score="joint_catalog_logits",
            rank_ties="stable_catalog_row",
            history_exclusion=False,
            alpha_policy=alpha_policy,
            alpha_source="fixed" if fixed_alpha is not None else "checkpoint",
            fixed_mixture_alpha=fixed_alpha,
        )

    @property
    def history_eligibility_contract(self):
        hybrid = self.prediction_mode == "hybrid"
        return dict(
            protocol=(
                "copmrec-hybrid-history-exclusion-off-v1" if hybrid else "copmrec-final-history-exclusion-off-v1"
            ),
            history_exclusion=False,
            history_representation="unchanged",
            score_rule="unchanged_candidate_joint_logits" if hybrid else "unchanged_full_catalog_logits",
            rank_ties="stable_catalog_row",
            cold_items_eligible=True,
            single_process=True,
        )

    def _joint_losses(self, target_ids, encoded, mask, query, rows, *, training=False, content_logits=None):
        if training and content_logits is not None:
            raise ValueError("Joint-only training requires its own shared catalog projection.")
        return super()._joint_losses(
            target_ids, encoded, mask, query, rows, training=training, content_logits=content_logits
        )

    @torch.no_grad()
    def retrieve(self, model_input, mode=None, target_ids=None):
        if mode not in (None, "dense", "hybrid") or target_ids is not None:
            raise ValueError("CoPMRec v2 requires dense/hybrid prediction without target traces.")
        return Liger.retrieve(self, model_input, mode=mode)

    def on_save_checkpoint(self, checkpoint):
        super().on_save_checkpoint(checkpoint)
        checkpoint["copmrec_formal_release"] = self.formal_release

    def on_load_checkpoint(self, checkpoint):
        release = checkpoint.get("copmrec_formal_release")
        expected = self.formal_release
        if (
            not isinstance(release, dict)
            or set(release) != set(expected)
            or any(type(release[key]) is not type(value) or release[key] != value for key, value in expected.items())
        ):
            raise ValueError("CoPMRec v2 requires its own joint-only formal checkpoint.")
        super().on_load_checkpoint(checkpoint)
