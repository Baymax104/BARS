"""当前两损失配方的匹配消融、零梯度连接与完整训练状态恢复。"""

import copy
from unittest.mock import patch

import pytest
import torch
import torch.distributed as dist
from copmrec_fixtures import copmrec, snapshot
from test_copmrec_untied_residual import checkpoint, optimizers, update
from test_liger import batch
from torch.nn.parallel import DistributedDataParallel

from src.recommendation.copmrec.ablation import CURRENT_M3_PROTOCOL, CURRENT_M3_VARIANTS, M3_PROTOCOL

FULL = "untied_fixed_alpha_half_no_mixture"
SHARED, ZERO, NO_CE = CURRENT_M3_VARIANTS


@pytest.mark.parametrize("variant", CURRENT_M3_VARIANTS)
def test_current_controls_match_initialization_dropout_stream_and_declared_objective(variant):
    options = dict(dropout=0.1, projection_dropout=0.1, input_dropout=0.1, validation_selection_mode="hybrid")
    torch.manual_seed(42)
    full = copmrec(FULL, **options)
    initial_rng = torch.get_rng_state()
    torch.manual_seed(42)
    actual = copmrec(variant, **options)
    assert torch.equal(torch.get_rng_state(), initial_rng)
    for name, value in actual.state_dict().items():
        torch.testing.assert_close(value, full.state_dict()[name], rtol=0, atol=0)
    inputs, labels = batch()
    torch.manual_seed(123)
    expected = full.losses(inputs, labels.target_ids, training=True)
    expected_rng = torch.get_rng_state()
    torch.manual_seed(123)
    values = actual.losses(inputs, labels.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), expected_rng)
    for name in ("sid_loss", "content_loss", "mixture_loss"):
        torch.testing.assert_close(values[name], expected[name], rtol=0, atol=0)
    objective = values["sid_loss"] if variant == NO_CE else values["sid_loss"] + values["content_loss"]
    torch.testing.assert_close(values["loss"], objective, rtol=0, atol=0)
    assert not values["mixture_loss"].requires_grad
    assert actual.ablation_contract["protocol"] == CURRENT_M3_PROTOCOL
    assert actual.formal_release["m3_protocol"] == CURRENT_M3_PROTOCOL
    assert actual.ablation_contract["loss_weights"] == dict(
        sid_ce=1, joint_catalog_ce=int(variant != NO_CE), mixture_nll=0
    )
    processor = actual.candidate_processor(torch.randn(2, 6))
    assert processor.gate is None and processor.alpha == 0.5
    assert actual.deployment_contract["alpha_source"] == "fixed"
    assert actual.deployment_contract["fixed_mixture_alpha"] == 0.5
    values["loss"].backward()
    assert actual.dynamic_gate.bias.grad is None and not actual.dynamic_gate.bias.requires_grad
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in actual.parameters() if p.requires_grad)
    residual = actual.collaborative_residual.weight
    if variant == ZERO:
        assert not residual.requires_grad and residual.grad is None
    elif variant == NO_CE:
        assert not torch.count_nonzero(residual.grad)
        assert actual.history_collaborative_residual.weight.grad.abs().sum() > 0
    else:
        assert residual.grad.abs().sum() > 0


@pytest.mark.parametrize("variant", CURRENT_M3_VARIANTS)
def test_current_own_restore_preserves_adam_steps_and_next_update(variant):
    actual, saved = snapshot(variant, updates=2, validation_selection_mode="hybrid")
    contract = saved["copmrec_unified_scratch"]
    assert contract["training_validation"] == "hybrid_beam_plus_all_cold"
    assert contract["alpha_policy"] == "frozen_0.5"
    assert contract["validation_retrieval"]["candidate_strategy"] == "probability_mixture"
    optimizer, scheduler = optimizers(actual)
    optimizer.load_state_dict(copy.deepcopy(saved["optimizer_states"][0]))
    scheduler.load_state_dict(copy.deepcopy(saved["lr_schedulers"][0]))
    restored = copmrec(variant, validation_selection_mode="hybrid")
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    restored_optimizer, restored_scheduler = optimizers(restored)
    restored_optimizer.load_state_dict(copy.deepcopy(saved["optimizer_states"][0]))
    restored_scheduler.load_state_dict(copy.deepcopy(saved["lr_schedulers"][0]))
    assert len(optimizer.param_groups) == (1 if variant == ZERO else 2)
    assert all(state["step"].item() == 2 for state in optimizer.state.values())
    if variant == NO_CE:
        weight = actual.collaborative_residual.weight
        assert not torch.count_nonzero(weight)
        assert not torch.count_nonzero(optimizer.state[weight]["exp_avg"])
        assert not torch.count_nonzero(optimizer.state[weight]["exp_avg_sq"])
    update(actual, optimizer, scheduler)
    update(restored, restored_optimizer, restored_scheduler)
    torch.testing.assert_close(restored.state_dict(), actual.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_optimizer.state_dict(), optimizer.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_scheduler.state_dict(), scheduler.state_dict(), rtol=0, atol=0)
    restored.on_load_checkpoint(checkpoint(restored, restored_optimizer, restored_scheduler, 3))
    with pytest.raises(ValueError):
        copmrec(variant, validation_selection_mode="dense").on_load_checkpoint(saved)


@pytest.mark.parametrize("variant", CURRENT_M3_VARIANTS)
def test_current_checkpoints_reject_other_controls_full_and_legacy_identity(variant):
    _, saved = snapshot(variant, validation_selection_mode="hybrid")
    for other in (FULL, "no_residual", "untied_no_joint_ce", *CURRENT_M3_VARIANTS):
        if other != variant:
            with pytest.raises(ValueError):
                copmrec(other, validation_selection_mode="hybrid").on_load_checkpoint(saved)


@pytest.mark.parametrize("variant", [FULL, *CURRENT_M3_VARIANTS])
def test_current_hybrid_sources_restore_strictly_for_inference_and_keep_original_m3_protocol(variant):
    actual, saved = snapshot(variant, updates=2, validation_selection_mode="hybrid")
    restored = copmrec(variant, training_model_config=None, validation_selection_mode="hybrid").eval()
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    actual.eval()
    with torch.no_grad():
        torch.testing.assert_close(restored.retrieve(batch()[0]), actual.retrieve(batch()[0]), rtol=0, atol=0)
    assert restored.unified_scratch_contract == saved["copmrec_unified_scratch"]
    assert restored.formal_release == saved["copmrec_formal_release"]
    assert restored.formal_release["m3_protocol"] == (M3_PROTOCOL if variant == FULL else CURRENT_M3_PROTOCOL)


@pytest.mark.parametrize("variant", [ZERO, NO_CE])
def test_zero_catalog_state_cannot_be_relabelled_after_training(variant):
    _, saved = snapshot(variant, validation_selection_mode="hybrid")
    saved["state_dict"]["collaborative_residual.weight"][0, 0] = 0.1
    with pytest.raises(ValueError, match="frozen zero state"):
        copmrec(variant, validation_selection_mode="hybrid").on_load_checkpoint(saved)


def test_no_catalog_ce_gradient_equals_sid_only_and_has_complete_adam_state():
    torch.manual_seed(42)
    actual = copmrec(NO_CE)
    inputs, labels = batch()
    values = actual.losses(inputs, labels.target_ids, training=True)
    parameters = [p for p in actual.parameters() if p.requires_grad]
    expected = torch.autograd.grad(values["sid_loss"], parameters, allow_unused=True, retain_graph=True)
    values["loss"].backward()
    for parameter, gradient in zip(parameters, expected, strict=True):
        torch.testing.assert_close(
            parameter.grad, torch.zeros_like(parameter) if gradient is None else gradient, rtol=0, atol=0
        )
    _, saved = snapshot(NO_CE, updates=3)
    assert len(saved["optimizer_states"][0]["state"]) == len(parameters)
    assert all(state["step"].item() == 3 for state in saved["optimizer_states"][0]["state"].values())


def test_zero_control_matches_independent_frozen_zero_tables_after_updates():
    options = dict(dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(42)
    actual = copmrec(ZERO, **options)
    torch.manual_seed(42)
    reference = copmrec(FULL, **options)
    for name in reference.residual_parameter_names:
        reference.get_parameter(name).requires_grad_(False)
    common = [p for p in reference.parameters() if p.requires_grad]
    with (
        patch.object(reference, "_optimizer_parameters", return_value=[common]),
        patch.object(reference, "_optimizer_peak_lrs", return_value=[reference.base_lr]),
    ):
        reference_optimizer, reference_scheduler = optimizers(reference)
    actual_optimizer, actual_scheduler = optimizers(actual)
    assert len(actual_optimizer.param_groups) == 1
    for step in range(3):
        torch.manual_seed(100 + step)
        update(actual, actual_optimizer, actual_scheduler)
        actual_rng = torch.get_rng_state()
        torch.manual_seed(100 + step)
        update(reference, reference_optimizer, reference_scheduler)
        assert torch.equal(torch.get_rng_state(), actual_rng)
        for name, parameter in actual.named_parameters():
            torch.testing.assert_close(parameter, reference.get_parameter(name), rtol=0, atol=0)
        torch.testing.assert_close(actual_optimizer.state_dict(), reference_optimizer.state_dict(), rtol=0, atol=0)
    assert not torch.count_nonzero(reference.history_collaborative_residual.weight)


def test_no_catalog_ce_runs_repeated_cpu_ddp_backwards_without_unused_parameters(tmp_path):
    if not dist.is_available() or not dist.is_gloo_available():
        pytest.skip("CPU Gloo process group is unavailable.")
    assert not dist.is_initialized()

    class Objective(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.model = copmrec(NO_CE)

        def forward(self, inputs, targets):
            return self.model.losses(inputs, targets, training=True)["loss"]

    try:
        dist.init_process_group("gloo", init_method=(tmp_path / "process_group").as_uri(), rank=0, world_size=1)
    except RuntimeError as error:
        if "unsupported gloo device" in str(error):
            pytest.skip("This PyTorch build cannot create a CPU Gloo device.")
        raise
    try:
        objective = DistributedDataParallel(Objective(), find_unused_parameters=False, broadcast_buffers=False)
        inputs, labels = batch()
        for _ in range(2):
            objective.zero_grad(set_to_none=True)
            objective(inputs, labels.target_ids).backward()
            assert all(p.grad is not None for p in objective.parameters() if p.requires_grad)
    finally:
        dist.destroy_process_group()
