"""v2 单组件训练消融；独立 scratch 与独立恢复身份。"""

import math

import torch

from src.recommendation.copmrec.module import CoPMRec

M3_PROTOCOL = "copmrec-v2-ablation-20261009-v1"
CURRENT_M3_PROTOCOL = "bars-fixed-half-hybrid-m3-20261023-v1"
CURRENT_M3_VARIANTS = (
    "shared_fixed_alpha_half_no_mixture",
    "no_residual_fixed_alpha_half_no_mixture",
    "untied_fixed_alpha_half_no_joint_ce_no_mixture",
)
VARIANTS = ("no_mixture", "no_residual", "no_joint_ce")
TRAINING_VARIANTS = (
    *VARIANTS,
    "fixed_alpha_one",
    "untied_residual",
    "untied_no_joint_ce",
    "untied_fixed_alpha_one",
    "untied_fixed_alpha_half",
    "untied_fixed_alpha_half_no_mixture",
    "untied_alpha_near_zero",
    *CURRENT_M3_VARIANTS,
)
UNTIED_VARIANTS = (
    "untied_residual",
    "untied_no_joint_ce",
    "untied_fixed_alpha_one",
    "untied_fixed_alpha_half",
    "untied_fixed_alpha_half_no_mixture",
    "untied_alpha_near_zero",
    "untied_fixed_alpha_half_no_joint_ce_no_mixture",
)
FIXED_ALPHA_ONE_VARIANTS = ("fixed_alpha_one", "untied_fixed_alpha_one")
FIXED_ALPHA_HALF_VARIANTS = ("untied_fixed_alpha_half", "untied_fixed_alpha_half_no_mixture", *CURRENT_M3_VARIANTS)
FIXED_ALPHA_VARIANTS = (*FIXED_ALPHA_ONE_VARIANTS, *FIXED_ALPHA_HALF_VARIANTS)
NO_MIXTURE_VARIANTS = ("no_mixture", "untied_fixed_alpha_half_no_mixture", *CURRENT_M3_VARIANTS)
NO_RESIDUAL_VARIANTS = ("no_residual", "no_residual_fixed_alpha_half_no_mixture")
NO_JOINT_CE_VARIANTS = ("no_joint_ce", "untied_no_joint_ce", "untied_fixed_alpha_half_no_joint_ce_no_mixture")
NEAR_ZERO_ALPHA = 0.0001


class CoPMRecAblation(CoPMRec):
    def __init__(self, *, variant, **kwargs):
        if variant not in TRAINING_VARIANTS:
            raise ValueError(f"Unknown v2 ablation: {variant!r}.")
        self.variant = variant
        super().__init__(**kwargs)
        if variant == "untied_alpha_near_zero":
            # 仅改变有限 gate 初值，不消耗随机数或改变原 sigmoid 参数化。
            with torch.no_grad():
                self.dynamic_gate.bias.fill_(self.initial_gate_logit)
        if variant == "no_mixture" or variant in FIXED_ALPHA_VARIANTS:
            self.dynamic_gate.bias.requires_grad_(False)
        if variant in NO_RESIDUAL_VARIANTS:
            self.collaborative_residual.weight.requires_grad_(False)
        if variant in UNTIED_VARIANTS:
            self.history_collaborative_residual = torch.nn.Embedding.from_pretrained(
                torch.zeros_like(self.collaborative_residual.weight), freeze=False
            )

    @property
    def initial_gate_logit(self):
        if self.variant == "untied_alpha_near_zero":
            return math.log(NEAR_ZERO_ALPHA / (1 - NEAR_ZERO_ALPHA))
        return super().initial_gate_logit

    @property
    def residual_parameter_names(self):
        names = super().residual_parameter_names
        return (*names, "history_collaborative_residual.weight") if self.variant in UNTIED_VARIANTS else names

    @property
    def residual_contract(self):
        contract = super().residual_contract
        if self.variant in UNTIED_VARIANTS:
            contract = {
                **contract,
                "protocol": "copmrec-untied-collaborative-residual-v1",
                "sharing": "independent_history_and_catalog_after_content_projection",
            }
        return contract

    def item_history_residual(self, rows):
        if self.variant not in UNTIED_VARIANTS:
            return super().item_history_residual(rows)
        return (
            self.history_collaborative_residual(rows).masked_fill(~self.seen_mask[rows, None], 0) * self.residual_scale
        )

    @property
    def mixture_alpha_policy(self):
        if self.variant in FIXED_ALPHA_HALF_VARIANTS:
            return "frozen_0.5"
        return "frozen_1" if self.variant in FIXED_ALPHA_ONE_VARIANTS else super().mixture_alpha_policy

    @property
    def fixed_mixture_alpha_value(self):
        if self.variant in FIXED_ALPHA_HALF_VARIANTS:
            return 0.5
        return 1.0 if self.variant in FIXED_ALPHA_ONE_VARIANTS else super().fixed_mixture_alpha_value

    def effective_mixture_alpha(self):
        if self.variant in FIXED_ALPHA_ONE_VARIANTS:
            return self.dynamic_gate.bias.new_ones(())
        if self.variant in FIXED_ALPHA_HALF_VARIANTS:
            return self.dynamic_gate.bias.new_full((), 0.5)
        return super().effective_mixture_alpha()

    def target_mixture_log_probs(self, generation, content):
        # 精确端点直接取内容条件质量，不使用 sigmoid 近似或无穷 gate。
        if self.variant in FIXED_ALPHA_ONE_VARIANTS:
            return content
        if self.variant in FIXED_ALPHA_HALF_VARIANTS:
            return torch.logaddexp(generation, content) - math.log(2)
        return super().target_mixture_log_probs(generation, content)

    @property
    def ablation_contract(self):
        return dict(
            protocol=CURRENT_M3_PROTOCOL if self.variant in CURRENT_M3_VARIANTS else M3_PROTOCOL,
            base_release="copmrec-v2",
            variant=self.variant,
            loss_weights=dict(
                sid_ce=1,
                joint_catalog_ce=int(self.variant not in NO_JOINT_CE_VARIANTS),
                mixture_nll=int(self.variant not in NO_MIXTURE_VARIANTS),
            ),
            alpha_policy="frozen_0.5" if self.variant == "no_mixture" else self.mixture_alpha_policy,
            residual_mode=(
                "untied_history_catalog"
                if self.variant in UNTIED_VARIANTS
                else "frozen_zero_both"
                if self.variant in NO_RESIDUAL_VARIANTS
                else "shared_history_catalog"
            ),
        )

    @property
    def formal_release(self):
        return {
            **super().formal_release,
            "evidence_phase": "ablation",
            "variant": self.variant,
            "m3_protocol": self.ablation_contract["protocol"],
        }

    @property
    def unified_scratch_contract(self):
        contract = {
            **super().unified_scratch_contract,
            "m3_ablation": self.ablation_contract,
            "loss_weights": self.ablation_contract["loss_weights"],
            "alpha_policy": self.ablation_contract["alpha_policy"],
            "residual_sharing": self.ablation_contract["residual_mode"],
        }
        if self.variant in NO_RESIDUAL_VARIANTS:
            contract["optimizer"] = {**contract["optimizer"], "residual_lr": None}
        if self.variant == "untied_alpha_near_zero":
            contract.update(
                initialization="random_recommender_near_zero_gate_and_zero_residual",
                alpha_initialization=dict(
                    parameterization="sigmoid_logit",
                    value=NEAR_ZERO_ALPHA,
                    logit=self.initial_gate_logit,
                ),
            )
        return contract

    def _optimizer_parameters(self):
        if self.variant in NO_RESIDUAL_VARIANTS:
            return [[p for p in self.parameters() if p.requires_grad]]
        return super()._optimizer_parameters()

    def _optimizer_peak_lrs(self):
        return [self.base_lr] if self.variant in NO_RESIDUAL_VARIANTS else super()._optimizer_peak_lrs()

    def item_content_residual(self, rows):
        residual = super().item_content_residual(rows)
        return torch.zeros_like(residual) if self.variant in NO_RESIDUAL_VARIANTS else residual

    def on_load_checkpoint(self, checkpoint):
        state = checkpoint.get("state_dict", {})
        zero_parameters = []
        if self.variant in NO_RESIDUAL_VARIANTS or self.variant == "untied_fixed_alpha_half_no_joint_ce_no_mixture":
            zero_parameters.append("collaborative_residual.weight")
        if self.variant == "no_mixture" or self.variant in FIXED_ALPHA_VARIANTS:
            zero_parameters.append("dynamic_gate.bias")
        if any(torch.count_nonzero(state.get(name, torch.ones(1))) for name in zero_parameters):
            raise ValueError("Disabled v2 component requires its frozen zero state.")
        super().on_load_checkpoint(checkpoint)

    def _joint_losses(self, *args, **kwargs):
        values = super()._joint_losses(*args, **kwargs)
        total = values["sid_loss"]
        if self.variant not in NO_JOINT_CE_VARIANTS:
            total = total + values["content_loss"]
        elif self.variant == "untied_fixed_alpha_half_no_joint_ce_no_mixture":
            # 总目标仍为 SID CE；零连接让目录零表获得零梯度，保持 DDP 和 Adam 同步数契约。
            total = total + 0.0 * values["content_loss"]
        if self.variant not in NO_MIXTURE_VARIANTS:
            total = total + values["mixture_loss"]
        else:
            values["mixture_loss"] = values["mixture_loss"].detach()
        values["loss"] = total
        return values
