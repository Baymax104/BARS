"""共同零残差对照的 CPU 数值等价；不重放原 DDP 全训练。"""

from unittest.mock import patch

import pytest
import torch
from copmrec_fixtures import copmrec
from test_liger import batch


@pytest.mark.parametrize("seed", [42, 200])
def test_legacy_no_residual_matches_independent_frozen_zero_tables(seed):
    options = dict(initialization_seed=seed, dropout=0.1, projection_dropout=0.1, input_dropout=0.1)
    torch.manual_seed(seed)
    legacy = copmrec("no_residual", **options)
    initial_rng = torch.get_rng_state().clone()
    torch.manual_seed(seed)
    reference = copmrec("untied_residual", **options)
    assert torch.equal(initial_rng, torch.get_rng_state())
    for name, value in legacy.state_dict().items():
        torch.testing.assert_close(value, reference.state_dict()[name], rtol=0, atol=0)

    frozen_tables = [reference.collaborative_residual.weight, reference.history_collaborative_residual.weight]
    assert frozen_tables[0].data_ptr() != frozen_tables[1].data_ptr()
    for weight in frozen_tables:
        weight.requires_grad_(False)
        assert not torch.count_nonzero(weight)
    common = [parameter for parameter in reference.parameters() if parameter.requires_grad]
    # 仅定义独立双零表的数值参考；不修改正式 variant 或 checkpoint 身份。
    with (
        patch.object(reference, "_optimizer_parameters", return_value=[common]),
        patch.object(reference, "_optimizer_peak_lrs", return_value=[reference.base_lr]),
    ):
        reference_configuration = reference.configure_optimizers()
    legacy_configuration = legacy.configure_optimizers()
    optimizer_pairs = [
        (model, config["optimizer"], config["lr_scheduler"]["scheduler"])
        for model, config in ((legacy, legacy_configuration), (reference, reference_configuration))
    ]
    assert [name for name, p in legacy.named_parameters() if p.requires_grad] == [
        name for name, p in reference.named_parameters() if p.requires_grad
    ]
    for _, optimizer, _ in optimizer_pairs:
        assert len(optimizer.param_groups) == 1
        assert optimizer.param_groups[0]["initial_lr"] == 0.0003
        assert optimizer.param_groups[0]["weight_decay"] == 0.035
        assert all(
            parameter is not weight
            for group in optimizer.param_groups
            for parameter in group["params"]
            for weight in frozen_tables
        )

    inputs, labels = batch()
    for step in range(5):
        values, rng_states = [], []
        for model, optimizer, scheduler in optimizer_pairs:
            model.train()
            optimizer.zero_grad(set_to_none=True)
            torch.manual_seed(1000 + step)
            losses = model.losses(inputs, labels.target_ids, training=True)
            values.append(losses)
            rng_states.append(torch.get_rng_state().clone())
            losses["loss"].backward()
            optimizer.step()
            scheduler.step()
        assert torch.equal(*rng_states)
        for name in ("sid_loss", "content_loss", "mixture_loss", "loss", "mixture_alpha"):
            torch.testing.assert_close(values[0][name], values[1][name], rtol=0, atol=0)
        for name, parameter in legacy.named_parameters():
            other = reference.get_parameter(name)
            torch.testing.assert_close(parameter, other, rtol=0, atol=0)
            if parameter.grad is not None:
                torch.testing.assert_close(parameter.grad, other.grad, rtol=0, atol=0)
        for weight in frozen_tables:
            assert weight.grad is None and not torch.count_nonzero(weight)
        torch.testing.assert_close(
            optimizer_pairs[0][1].state_dict(), optimizer_pairs[1][1].state_dict(), rtol=0, atol=0
        )
        torch.testing.assert_close(
            optimizer_pairs[0][2].state_dict(), optimizer_pairs[1][2].state_dict(), rtol=0, atol=0
        )

    legacy.eval()
    reference.eval()
    for mode in ("dense", "hybrid"):
        torch.testing.assert_close(legacy.retrieve(inputs, mode), reference.retrieve(inputs, mode), rtol=0, atol=0)
