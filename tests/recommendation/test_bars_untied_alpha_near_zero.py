"""有限负 logit 只改变 alpha 初值，保留联合训练和完整恢复协议。"""

import copy
import math
from types import SimpleNamespace

import pytest
import torch
from bars_fixtures import bars, snapshot
from test_bars_untied_residual import checkpoint, optimizers, residual_weights, update
from test_liger import batch

from src.recommendation.bars.ablation import NEAR_ZERO_ALPHA, TRAINING_VARIANTS

VARIANT = "untied_alpha_near_zero"


def attach_trainer(model, optimizer, scheduler, step=0):
    model._trainer = SimpleNamespace(
        max_steps=50000,
        limit_train_batches=1.0,
        limit_val_batches=1.0,
        datamodule=SimpleNamespace(
            get_stage_config=lambda stage: SimpleNamespace(batch_size_per_device=128, drop_last=True)
        ),
        world_size=2,
        accumulate_grad_batches=1,
        val_check_interval=500,
        gradient_clip_val=1,
        precision="32-true",
        optimizers=[optimizer],
        lr_scheduler_configs=[SimpleNamespace(scheduler=scheduler)],
        global_step=step,
    )


def test_near_zero_only_changes_gate_initialization_without_consuming_rng():
    options = dict(initialization_seed=200, dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(200)
    baseline = bars("untied_residual", **options)
    expected_rng = torch.get_rng_state()
    torch.manual_seed(200)
    actual = bars(VARIANT, **options)
    assert torch.equal(torch.get_rng_state(), expected_rng)
    for name, value in baseline.state_dict().items():
        if name != "dynamic_gate.bias":
            torch.testing.assert_close(actual.state_dict()[name], value, rtol=0, atol=0)
    assert actual.dynamic_gate.bias.requires_grad
    assert torch.isfinite(actual.dynamic_gate.bias)
    assert actual.dynamic_gate.bias.item() == pytest.approx(math.log(0.0001 / 0.9999))
    assert actual.effective_mixture_alpha().item() == pytest.approx(NEAR_ZERO_ALPHA)
    catalog, history = residual_weights(actual)
    assert catalog.data_ptr() != history.data_ptr()
    assert not torch.count_nonzero(catalog) and not torch.count_nonzero(history)

    inputs, labels = batch()
    torch.manual_seed(100)
    expected = baseline.losses(inputs, labels.target_ids, training=True)
    expected_rng = torch.get_rng_state()
    torch.manual_seed(100)
    values = actual.losses(inputs, labels.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), expected_rng)
    for name in ("sid_loss", "content_loss"):
        torch.testing.assert_close(values[name], expected[name], rtol=0, atol=0)


def test_near_zero_keeps_trainable_stable_mixture_and_matching_inference():
    actual = bars(VARIANT)
    generation = torch.tensor([[-0.2], [-2.0]], requires_grad=True)
    content = torch.tensor([[-1.4], [-0.4]], requires_grad=True)
    mixed = actual.target_mixture_log_probs(generation, content)
    alpha = actual.dynamic_gate.bias.sigmoid()
    expected = ((1 - alpha) * generation.exp() + alpha * content.exp()).log()
    torch.testing.assert_close(mixed, expected)
    (-mixed.sum()).backward()
    for parameter in (generation, content, actual.dynamic_gate.bias):
        assert parameter.grad is not None and torch.isfinite(parameter.grad).all()
        assert parameter.grad.abs().sum() > 0

    processor = actual.candidate_processor(torch.randn(2, 6))
    assert processor.gate is actual.dynamic_gate
    prefix, scores = torch.zeros(2, 1, dtype=torch.long), torch.randn(2, 7)
    _, gen, mass, _ = processor.distributions(prefix, scores)
    torch.testing.assert_close(processor(prefix, scores)[:, 1:4], actual.target_mixture_log_probs(gen, mass))
    assert actual.deployment_contract["alpha_policy"] == "learned"
    assert actual.deployment_contract["alpha_source"] == "checkpoint"
    assert actual.deployment_contract["fixed_mixture_alpha"] is None


def test_near_zero_three_losses_train_both_residuals_and_use_unchanged_optimizer_groups():
    actual = bars(VARIANT)
    values = actual.losses(batch()[0], batch()[1].target_ids, training=True)
    torch.testing.assert_close(values["loss"], values["sid_loss"] + values["content_loss"] + values["mixture_loss"])
    values["mixture_loss"].backward()
    assert actual.dynamic_gate.bias.grad.abs().sum() > 0
    assert actual.transformer.decoder.block[0].layer[0].SelfAttention.q.weight.grad.abs().sum() > 0
    for weight in residual_weights(actual):
        assert weight.grad is not None and torch.isfinite(weight.grad).all()
        assert weight.grad[actual.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight.grad[~actual.seen_mask])

    optimizer, scheduler = optimizers(actual)
    assert [group["initial_lr"] for group in optimizer.param_groups] == [0.0003, 0.002]
    assert all(group["weight_decay"] == 0.035 for group in optimizer.param_groups)
    assert any(p is actual.dynamic_gate.bias for p in optimizer.param_groups[0]["params"])
    assert len(optimizer.param_groups[1]["params"]) == 2
    for weight in residual_weights(actual):
        assert any(p is weight for p in optimizer.param_groups[1]["params"])
    initial_logit = actual.dynamic_gate.bias.detach().clone()
    # warmup 最初几步的更新小于该负 logit 的 FP32 ULP。
    for _ in range(12):
        update(actual, optimizer, scheduler)
    assert not torch.equal(actual.dynamic_gate.bias, initial_logit)
    assert 0 < actual.effective_mixture_alpha().item() < 1
    for weight in residual_weights(actual):
        assert weight[actual.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight[~actual.seen_mask])


@pytest.mark.parametrize("fault", [None, "gate_zero", "gate_shift", "catalog", "history"])
def test_fresh_fit_requires_prescribed_near_zero_gate_and_zero_residuals(fault):
    actual = bars(VARIANT)
    optimizer, scheduler = optimizers(actual)
    attach_trainer(actual, optimizer, scheduler)
    actual.on_fit_start()
    with torch.no_grad():
        if fault == "gate_zero":
            actual.dynamic_gate.bias.zero_()
        elif fault == "gate_shift":
            actual.dynamic_gate.bias.add_(0.1)
        elif fault in {"catalog", "history"}:
            residual_weights(actual)[int(fault == "history")][0, 0] = 1
    if fault is None:
        actual.on_train_start()
        actual.on_train_batch_start(batch(), 0)
    else:
        with pytest.raises(ValueError, match="zero residual and gate initialization"):
            actual.on_train_start()


@pytest.mark.parametrize("variant", [None, *(v for v in TRAINING_VARIANTS if v != VARIANT)])
def test_legacy_variants_keep_their_zero_gate_expectation_and_existing_contract(variant):
    actual = bars(variant)
    assert actual.initial_gate_logit == 0.0
    assert not torch.count_nonzero(actual.dynamic_gate.bias)
    contract = actual.unified_scratch_contract
    assert contract["initialization"] == "random_recommender_zero_gate_and_residual"
    assert "alpha_initialization" not in contract
    optimizer, scheduler = optimizers(actual)
    attach_trainer(actual, optimizer, scheduler)
    actual.on_fit_start()
    with torch.no_grad():
        actual.dynamic_gate.bias.fill_(math.log(0.0001 / 0.9999))
    with pytest.raises(ValueError, match="zero residual and gate initialization"):
        actual.on_train_start()


def test_near_zero_own_restore_preserves_contract_and_next_continuous_update():
    torch.manual_seed(42)
    actual = bars(VARIANT)
    optimizer, scheduler = optimizers(actual)
    for _ in range(12):
        update(actual, optimizer, scheduler)
    saved = checkpoint(actual, optimizer, scheduler, 12)
    contract = saved["copmrec_unified_scratch"]
    assert contract["initialization"] == "random_recommender_near_zero_gate_and_zero_residual"
    assert contract["alpha_initialization"] == dict(
        parameterization="sigmoid_logit", value=0.0001, logit=math.log(0.0001 / 0.9999)
    )
    assert contract["loss_weights"] == dict(sid_ce=1, joint_catalog_ce=1, mixture_nll=1)
    assert contract["alpha_policy"] == "learned"
    assert contract["residual_sharing"] == "untied_history_catalog"
    assert saved["copmrec_alpha_policy"] == "learned"
    assert saved["copmrec_fixed_mixture_alpha"] is None

    restored = bars(VARIANT)
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    restored_optimizer, restored_scheduler = optimizers(restored)
    restored_optimizer.load_state_dict(copy.deepcopy(saved["optimizer_states"][0]))
    restored_scheduler.load_state_dict(copy.deepcopy(saved["lr_schedulers"][0]))
    assert restored.restored_step == 12
    assert not torch.equal(
        restored.dynamic_gate.bias, restored.dynamic_gate.bias.new_full((), restored.initial_gate_logit)
    )
    attach_trainer(restored, restored_optimizer, restored_scheduler, step=12)
    restored.on_fit_start()
    restored.on_train_start()
    update(actual, optimizer, scheduler)
    update(restored, restored_optimizer, restored_scheduler)
    torch.testing.assert_close(restored.state_dict(), actual.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_optimizer.state_dict(), optimizer.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_scheduler.state_dict(), scheduler.state_dict(), rtol=0, atol=0)
    bars(VARIANT).on_load_checkpoint(checkpoint(restored, restored_optimizer, restored_scheduler, 13))


@pytest.mark.parametrize("other", [None, *(v for v in TRAINING_VARIANTS if v != VARIANT)])
def test_near_zero_checkpoint_cannot_restore_as_other_variants_in_either_direction(other):
    _, saved = snapshot(VARIANT)
    _, other_saved = snapshot(other)
    with pytest.raises(ValueError):
        bars(other).on_load_checkpoint(saved)
    with pytest.raises(ValueError):
        bars(VARIANT).on_load_checkpoint(other_saved)


@pytest.mark.parametrize("fault", ["missing_init", "alpha", "logit", "parameterization", "nan_gate", "moments"])
def test_near_zero_restore_rejects_corrupted_initialization_or_training_state(fault):
    _, saved = snapshot(VARIANT)
    initialization = saved["copmrec_unified_scratch"]["alpha_initialization"]
    if fault == "missing_init":
        del saved["copmrec_unified_scratch"]["alpha_initialization"]
    elif fault == "alpha":
        initialization["value"] = 0.5
    elif fault == "logit":
        initialization["logit"] = 0.0
    elif fault == "parameterization":
        initialization["parameterization"] = "projected_probability"
    elif fault == "nan_gate":
        saved["state_dict"]["dynamic_gate.bias"].fill_(torch.nan)
    else:
        saved["optimizer_states"][0]["state"].clear()
    with pytest.raises(ValueError):
        bars(VARIANT).on_load_checkpoint(saved)
