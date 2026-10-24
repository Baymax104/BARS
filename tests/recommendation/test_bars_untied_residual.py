"""用真实 CPU 小模型验证残差拆分、匹配优化和完整恢复。"""

import copy
from types import SimpleNamespace

import pytest
import torch
from bars_fixtures import bars, snapshot
from test_liger import batch

TABLE_NAMES = ("collaborative_residual", "history_collaborative_residual")
OLD_VARIANTS = (None, "no_mixture", "no_residual", "no_joint_ce", "fixed_alpha_one")
LOSS_NAMES = ("sid_loss", "content_loss", "mixture_loss", "loss")


def residual_weights(model):
    return [getattr(model, name).weight for name in TABLE_NAMES]


def optimizers(model):
    result = model.configure_optimizers()
    return result["optimizer"], result["lr_scheduler"]["scheduler"]


def update(model, optimizer, scheduler):
    model.zero_grad(set_to_none=True)
    inputs, labels = batch()
    model.losses(inputs, labels.target_ids, training=True)["loss"].backward()
    optimizer.step()
    scheduler.step()


def checkpoint(model, optimizer, scheduler, step):
    saved = dict(
        global_step=step,
        state_dict=copy.deepcopy(model.state_dict()),
        optimizer_states=[copy.deepcopy(optimizer.state_dict())],
        lr_schedulers=[copy.deepcopy(scheduler.state_dict())],
    )
    model.on_save_checkpoint(saved)
    return saved


@pytest.fixture(scope="module")
def untied_checkpoint():
    return snapshot("untied_residual", updates=2)[1]


def test_untied_preserves_public_initialization_losses_and_dropout_rng():
    options = dict(initialization_seed=200, dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(200)
    full = bars(**options)
    full_rng = torch.get_rng_state()
    torch.manual_seed(200)
    untied = bars("untied_residual", **options)
    assert torch.equal(torch.get_rng_state(), full_rng)
    for name, value in full.state_dict().items():
        torch.testing.assert_close(untied.state_dict()[name], value, rtol=0, atol=0)
    catalog, history = residual_weights(untied)
    assert catalog.data_ptr() != history.data_ptr()
    assert catalog.shape == history.shape and not torch.count_nonzero(catalog) and not torch.count_nonzero(history)
    parameter_delta = sum(p.numel() for p in untied.parameters()) - sum(p.numel() for p in full.parameters())
    assert parameter_delta == history.numel()

    inputs, labels = batch()
    torch.manual_seed(100)
    full_values = full.losses(inputs, labels.target_ids, training=True)
    full_rng = torch.get_rng_state()
    torch.manual_seed(100)
    untied_values = untied.losses(inputs, labels.target_ids, training=True)
    assert torch.equal(torch.get_rng_state(), full_rng)
    for name in (*LOSS_NAMES, "mixture_alpha"):
        torch.testing.assert_close(untied_values[name], full_values[name], rtol=0, atol=0)
    torch.testing.assert_close(
        untied_values["loss"], sum(untied_values[name] for name in LOSS_NAMES[:-1]), rtol=0, atol=0
    )


@pytest.mark.parametrize("table_name", TABLE_NAMES)
def test_each_table_affects_only_its_own_direct_path(table_name):
    actual = bars("untied_residual").eval()
    inputs, _ = batch()
    query = actual.encode(inputs.input_ids, inputs.attention_mask)[2].detach()
    logits = actual.dense_logits(query).detach()
    with torch.no_grad():
        # 第一条 history 的末个商品直接参与 query，避免依赖随机注意力的微小传播。
        getattr(actual, table_name).weight[1].add_(torch.arange(8).float() / 3 - 1)
    changed_query = actual.encode(inputs.input_ids, inputs.attention_mask)[2].detach()
    changed_logits = actual.dense_logits(query).detach()
    if table_name == "collaborative_residual":
        torch.testing.assert_close(changed_query, query, rtol=0, atol=0)
        assert not torch.allclose(changed_logits, logits)
    else:
        assert not torch.allclose(changed_query, query)
        torch.testing.assert_close(changed_logits, logits, rtol=0, atol=0)


@pytest.mark.parametrize("loss_name", LOSS_NAMES)
def test_shared_gradient_equals_sum_of_untied_role_gradients(loss_name):
    torch.manual_seed(42)
    full = bars()
    torch.manual_seed(42)
    untied = bars("untied_residual")
    inputs, labels = batch()
    full.losses(inputs, labels.target_ids, training=True)[loss_name].backward()
    untied.losses(inputs, labels.target_ids, training=True)[loss_name].backward()
    expected = sum(
        weight.grad if weight.grad is not None else torch.zeros_like(weight) for weight in residual_weights(untied)
    )
    assert torch.isfinite(expected).all()
    torch.testing.assert_close(full.collaborative_residual.weight.grad, expected, atol=2e-6, rtol=2e-5)


@pytest.mark.parametrize("loss_name", LOSS_NAMES[:-1])
def test_declared_losses_reach_the_expected_residual_roles(loss_name):
    actual = bars("untied_residual")
    inputs, labels = batch()
    actual.losses(inputs, labels.target_ids, training=True)[loss_name].backward()
    catalog, history = residual_weights(actual)
    active = [history] if loss_name == "sid_loss" else [catalog, history]
    if loss_name == "sid_loss":
        assert catalog.grad is None
    for weight in active:
        assert weight.grad is not None and torch.isfinite(weight.grad).all()
        assert weight.grad[actual.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight.grad[~actual.seen_mask])
    assert actual.content_projection.output.weight.grad.abs().sum() > 0
    if loss_name == "mixture_loss":
        assert actual.dynamic_gate.bias.grad is not None and torch.isfinite(actual.dynamic_gate.bias.grad).all()
        assert actual.dynamic_gate.bias.grad.abs().sum() > 0


def test_both_tables_use_residual_optimizer_group_and_keep_cold_zero():
    actual = bars("untied_residual")
    optimizer, scheduler = optimizers(actual)
    weights = residual_weights(actual)
    groups = optimizer.param_groups
    assert len(groups) == 2
    assert [group["initial_lr"] for group in groups] == [0.0003, 0.002]
    for weight in weights:
        assert sum(parameter is weight for group in groups for parameter in group["params"]) == 1
        assert any(parameter is weight for parameter in groups[1]["params"])
        assert all(parameter is not weight for parameter in groups[0]["params"])
    assert all(group["weight_decay"] == 0.035 for group in groups)
    for _ in range(2):
        update(actual, optimizer, scheduler)
    for weight in weights:
        assert weight[actual.seen_mask].abs().sum() > 0
        assert not torch.count_nonzero(weight[~actual.seen_mask])
        assert weight.grad is not None and not torch.count_nonzero(weight.grad[~actual.seen_mask])
        moment = optimizer.state[weight]
        assert moment["step"].item() == 2
        assert moment["exp_avg"].abs().sum() > 0 and moment["exp_avg_sq"].abs().sum() > 0
    assert optimizer.state[weights[0]]["exp_avg"].data_ptr() != optimizer.state[weights[1]]["exp_avg"].data_ptr()
    rows = torch.arange(len(actual.item_keys))
    assert not torch.count_nonzero(actual.item_content_residual(rows)[~actual.seen_mask])
    assert not torch.count_nonzero(actual.item_history_residual(rows)[~actual.seen_mask])


def test_full_optimizer_and_scheduler_restore_matches_next_continuous_update():
    torch.manual_seed(42)
    actual = bars("untied_residual")
    optimizer, scheduler = optimizers(actual)
    for _ in range(2):
        update(actual, optimizer, scheduler)
    saved = checkpoint(actual, optimizer, scheduler, 2)

    restored = bars("untied_residual")
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    restored_optimizer, restored_scheduler = optimizers(restored)
    restored_optimizer.load_state_dict(copy.deepcopy(saved["optimizer_states"][0]))
    restored_scheduler.load_state_dict(copy.deepcopy(saved["lr_schedulers"][0]))
    assert restored.restored_step == 2
    update(actual, optimizer, scheduler)
    update(restored, restored_optimizer, restored_scheduler)
    torch.testing.assert_close(restored.state_dict(), actual.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_optimizer.state_dict(), optimizer.state_dict(), rtol=0, atol=0)
    torch.testing.assert_close(restored_scheduler.state_dict(), scheduler.state_dict(), rtol=0, atol=0)
    # 继续更新后的完整状态也必须通过真实 strict 恢复门禁。
    bars("untied_residual").on_load_checkpoint(checkpoint(restored, restored_optimizer, restored_scheduler, 3))


@pytest.mark.parametrize("corrupt_table", [None, *TABLE_NAMES])
def test_fresh_fit_checks_zero_initialization_of_both_tables(corrupt_table):
    actual = bars("untied_residual")
    optimizer, scheduler = optimizers(actual)
    actual._trainer = SimpleNamespace(
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
        global_step=0,
    )
    actual.on_fit_start()
    if corrupt_table is None:
        actual.on_train_start()
        actual.on_train_batch_start(batch(), 0)
    else:
        with torch.no_grad():
            getattr(actual, corrupt_table).weight[0, 0] = 1
        with pytest.raises(ValueError, match="zero residual"):
            actual.on_train_start()


@pytest.mark.parametrize("table_name", TABLE_NAMES)
@pytest.mark.parametrize("fault", ["missing", "shape", "dtype", "nonfinite", "cold"])
def test_restore_rejects_corrupted_residual_table(untied_checkpoint, table_name, fault):
    saved = copy.deepcopy(untied_checkpoint)
    state = saved["state_dict"]
    name = table_name + ".weight"
    if fault == "missing":
        del state[name]
    elif fault == "shape":
        state[name] = state[name][:-1]
    elif fault == "dtype":
        state[name] = state[name].double()
    elif fault == "nonfinite":
        state[name][0, 0] = float("nan")
    else:
        state[name][-1, 0] = 1
    with pytest.raises(ValueError):
        bars("untied_residual").on_load_checkpoint(saved)


@pytest.mark.parametrize("table_index", [0, 1])
@pytest.mark.parametrize("fault", ["missing", "shape", "dtype", "nonfinite", "step"])
def test_restore_rejects_corrupted_residual_optimizer_moment(untied_checkpoint, table_index, fault):
    saved = copy.deepcopy(untied_checkpoint)
    optimizer = saved["optimizer_states"][0]
    parameter = optimizer["param_groups"][1]["params"][table_index]
    moment = optimizer["state"][parameter]
    if fault == "missing":
        del optimizer["state"][parameter]
    elif fault == "shape":
        moment["exp_avg"] = moment["exp_avg"][:-1]
    elif fault == "dtype":
        moment["exp_avg_sq"] = moment["exp_avg_sq"].double()
    elif fault == "nonfinite":
        moment["exp_avg"][0, 0] = float("inf")
    else:
        moment["step"] -= 1
    with pytest.raises(ValueError):
        bars("untied_residual").on_load_checkpoint(saved)


@pytest.mark.parametrize("fault", ["group", "duplicate", "lr", "weight_decay", "scheduler"])
def test_restore_rejects_corrupted_dual_table_training_state(untied_checkpoint, fault):
    saved = copy.deepcopy(untied_checkpoint)
    groups = saved["optimizer_states"][0]["param_groups"]
    if fault == "group":
        groups[0]["params"].append(groups[1]["params"].pop())
    elif fault == "duplicate":
        groups[1]["params"][1] = groups[1]["params"][0]
    elif fault == "lr":
        groups[1]["lr"] = groups[0]["lr"]
    elif fault == "weight_decay":
        groups[1]["weight_decay"] = 0
    else:
        saved["lr_schedulers"][0]["base_lrs"] = [0.0003, 0.0003]
    with pytest.raises(ValueError):
        bars("untied_residual").on_load_checkpoint(saved)


@pytest.mark.parametrize("fault", ["variant", "residual_protocol", "residual_sharing", "scratch_sharing"])
def test_restore_rejects_relabelled_untied_checkpoint(untied_checkpoint, fault):
    saved = copy.deepcopy(untied_checkpoint)
    if fault == "variant":
        saved["copmrec_formal_release"]["variant"] = "no_joint_ce"
    elif fault == "residual_protocol":
        saved["copmrec_collaborative_residual"]["protocol"] = "copmrec-shared-collaborative-residual-v1"
    elif fault == "residual_sharing":
        saved["copmrec_collaborative_residual"]["sharing"] = "history_and_catalog_after_content_projection"
    else:
        saved["copmrec_unified_scratch"]["residual_sharing"] = "shared_history_catalog"
    with pytest.raises(ValueError):
        bars("untied_residual").on_load_checkpoint(saved)


@pytest.mark.parametrize("variant", OLD_VARIANTS)
def test_old_shared_checkpoints_remain_compatible_and_isolated(untied_checkpoint, variant):
    original, saved = snapshot(variant)
    assert "history_collaborative_residual.weight" not in saved["state_dict"]
    assert saved["copmrec_collaborative_residual"] == dict(
        protocol="copmrec-shared-collaborative-residual-v1",
        residual_scale=1.0,
        embedding_dim=original.transformer.config.d_model,
        catalog_size=len(original.item_keys),
        sharing="history_and_catalog_after_content_projection",
        cold_policy="seen_mask_zero",
    )
    restored = bars(variant, training_model_config=None).eval()
    restored.on_load_checkpoint(saved)
    restored.load_state_dict(saved["state_dict"], strict=True)
    torch.testing.assert_close(restored.retrieve(batch()[0])[0], original.eval().retrieve(batch()[0])[0])
    with pytest.raises(ValueError):
        bars("untied_residual").on_load_checkpoint(saved)
    with pytest.raises(ValueError):
        bars(variant).on_load_checkpoint(copy.deepcopy(untied_checkpoint))
