"""小型 CPU 模型验证共享监督、合法 beam、公共输出及 checkpoint 身份。"""

import copy
from functools import partial
from types import SimpleNamespace

import pytest
import torch
from torch.nn import functional as F

from src.common.configs.model import TrainingModelConfig
from src.data.components.data_models import TigerLabelData, TigerModelInput
from src.recommendation.intrr.module import IntrrRecommender


def catalog(sids=None, codebook_size=2):
    sids = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]]) if sids is None else torch.tensor(sids)
    return SimpleNamespace(
        keys=torch.arange(len(sids)) * 10 + 10,
        semantic_ids=sids,
        num_hierarchies=sids.shape[1],
        codebook_size=codebook_size,
        sha256=f"fixture-{sids.tolist()}",
    )


def model(catalog_data=None, **overrides):
    torch.manual_seed(23)
    arguments = dict(
        catalog=catalog_data or catalog(),
        sequence_length=18,
        embedding_dim=8,
        item_embedding_dim=6,
        ran_hidden_dim=10,
        num_layers=1,
        num_heads=2,
        d_kv=4,
        feedforward_dim=16,
        dropout=0,
        top_k_for_generation=4,
    )
    arguments.update(overrides)
    return IntrrRecommender(**arguments)


def inputs():
    return TigerModelInput(
        input_ids=torch.tensor([[0, 1, 0], [2, -1, -1]]),
        attention_mask=torch.tensor([[1, 1, 1], [1, 0, 0]]),
        output_keys=torch.tensor([101, 202]),
    )


def labels():
    return TigerLabelData(target_ids=torch.tensor([[0, 1], [1, 0]]))


def test_alignment_is_position_weighted_and_loss_preserves_author_layer_sum():
    recommender = model(alignment_weight=0.1)
    batch = inputs()
    values = recommender.losses(batch, labels().target_ids)
    valid_ids = batch.input_ids[batch.attention_mask.bool()]
    _, logits = recommender.ran(recommender.input_mlp(recommender.item_embedding(valid_ids)))
    targets = recommender.semantic_ids[valid_ids]
    expected = (
        torch.stack([F.cross_entropy(logits[:, level], targets[:, level], reduction="none") for level in range(2)], 1)
        .sum(1)
        .mean()
    )
    torch.testing.assert_close(values["alignment_loss"], expected)
    unique = valid_ids.unique()
    _, unique_logits = recommender.ran(recommender.input_mlp(recommender.item_embedding(unique)))
    unique_loss = F.cross_entropy(unique_logits.flatten(0, 1), recommender.semantic_ids[unique].flatten()) * 2
    assert not torch.allclose(expected, unique_loss)
    torch.testing.assert_close(values["loss"], values["sid_loss"] + 0.1 * expected)
    user_state, _ = recommender.encode_history(batch)
    _, user_logits = recommender.ran(user_state, labels().target_ids)
    expected_sid = sum(F.cross_entropy(user_logits[:, level], labels().target_ids[:, level]) for level in range(2))
    torch.testing.assert_close(values["sid_loss"], expected_sid)


def test_one_shared_ran_handles_uid_and_user_states_with_all_live_gradients():
    recommender = model()
    calls = []
    handle = recommender.ran.register_forward_hook(
        lambda module, args, output: calls.append((id(module), args[0].shape))
    )
    result = recommender.training_step((inputs(), labels()), 0)
    handle.remove()
    assert calls == [(id(recommender.ran), torch.Size([3, 8])), (id(recommender.ran), torch.Size([2, 8]))]
    result["loss"].backward()
    for parameter in recommender.parameters():
        if parameter.requires_grad:
            assert parameter.grad is not None and torch.isfinite(parameter.grad).all()


def enumerate_scores(recommender, user_state):
    """从单路径公式逐条枚举；不调用 generate、step 或其合法查询。"""
    output = []
    for sid in recommender.semantic_ids.tolist():
        score = user_state.new_zeros(())
        for level, token in enumerate(sid):
            if level == 0:
                hidden = user_state
            else:
                previous = recommender.ran.codebooks[level - 1][sid[level - 1]]
                hidden = recommender.ran.transitions[level - 1](torch.cat([previous, user_state], -1))
            logits = hidden @ recommender.ran.codebooks[level].T
            legal_tokens = {row[level] for row in recommender.semantic_ids.tolist() if row[:level] == sid[:level]}
            legal = torch.tensor([index in legal_tokens for index in range(recommender.codebook_size)])
            score = score + logits.masked_fill(~legal, -torch.inf).log_softmax(-1)[token]
        output.append((sid, score))
    output.sort(key=lambda value: value[1].item(), reverse=True)
    return torch.tensor([value[0] for value in output]), torch.stack([value[1] for value in output])


@pytest.mark.parametrize("narrow", [False, True])
def test_beam_matches_complete_path_enumeration_and_handles_narrow_tree(narrow):
    data = catalog([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]], 3) if narrow else catalog()
    recommender = model(data, top_k_for_generation=10).eval()
    batch = inputs()
    user_states, _ = recommender.encode_history(batch)
    generated, scores = recommender.generate(batch)
    for row, user_state in enumerate(user_states):
        expected_ids, expected_scores = enumerate_scores(recommender, user_state)
        torch.testing.assert_close(generated[row], expected_ids)
        torch.testing.assert_close(scores[row], expected_scores)
        assert len(generated[row].unique(dim=0)) == len(data.keys)
        assert torch.isfinite(scores[row]).all()


def test_eval_and_prediction_match_tiger_metric_and_writer_contract():
    recommender = model().eval()
    result = recommender.validation_step((inputs(), labels()), 0)
    assert {"loss", "generated_ids", "marginal_probs", "labels"} <= result.keys()
    assert result["generated_ids"].shape == (2, 4, 2)
    torch.testing.assert_close(result["labels"], labels().target_ids)
    output = recommender.predict_step((inputs(), None))
    assert output.keys.tolist() == [101, 202]
    assert output.predictions.device.type == "cpu"
    torch.testing.assert_close(output.predictions, result["generated_ids"])
    no_key = inputs()
    no_key.output_keys = None
    with pytest.raises(ValueError, match="output_keys"):
        recommender.predict_step(no_key)


def test_checkpoint_roundtrip_and_strict_identity():
    recommender = model().eval()
    checkpoint = {"state_dict": copy.deepcopy(recommender.state_dict())}
    recommender.on_save_checkpoint(checkpoint)
    restored = model().eval()
    restored.on_load_checkpoint(checkpoint)
    restored.load_state_dict(checkpoint["state_dict"], strict=True)
    torch.testing.assert_close(recommender.generate(inputs())[1], restored.generate(inputs())[1], rtol=0, atol=0)
    for changed in (
        model(alignment_weight=0),
        model(sequence_length=20),
        model(catalog_data=catalog([[1, 0], [1, 1], [0, 0], [0, 1]])),
    ):
        with pytest.raises(ValueError, match="identity"):
            changed.on_load_checkpoint(checkpoint)
    with pytest.raises(ValueError, match="identity"):
        restored.on_load_checkpoint({})


@pytest.mark.parametrize("method", ["validation_step", "test_step"])
@pytest.mark.parametrize("narrow", [False, True])
def test_evaluation_reuses_one_history_encoding_with_exact_legacy_outputs(method, narrow):
    data = (
        catalog([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]], 3)
        if narrow
        else catalog([[first, second] for first in range(4) for second in range(4)], 4)
    )
    recommender = model(data, dropout=0.15, top_k_for_generation=10).eval()
    reference = copy.deepcopy(recommender)
    batch = inputs()
    target = TigerLabelData(target_ids=data.semantic_ids[torch.tensor([1, 2])])
    calls = []
    handle = recommender.backbone.register_forward_hook(lambda *args: calls.append(1))
    try:
        with torch.inference_mode():
            expected = reference.losses(batch, target.target_ids)
            expected["generated_ids"], expected["marginal_probs"] = reference.generate(batch)
            expected["labels"] = target.target_ids
            actual = getattr(recommender, method)((batch, target), 0)
    finally:
        handle.remove()
    for key in expected:
        torch.testing.assert_close(actual[key], expected[key], rtol=0, atol=0)
    assert actual["generated_ids"].shape[1] == (5 if narrow else 10)
    assert calls == [1]


def test_external_optimizer_scheduler_are_injected_and_update_parameters():
    config = TrainingModelConfig(
        optimizer=partial(torch.optim.Adam, lr=0.001), scheduler=partial(torch.optim.lr_scheduler.StepLR, step_size=1)
    )
    recommender = model(training_model_config=config)
    configured = recommender.configure_optimizers()
    optimizer = configured["optimizer"]
    before = recommender.item_embedding.weight.detach().clone()
    recommender.training_step((inputs(), labels()), 0)["loss"].backward()
    optimizer.step()
    configured["lr_scheduler"]["scheduler"].step()
    assert not torch.equal(before, recommender.item_embedding.weight)
    assert configured["lr_scheduler"]["interval"] == "step"


@pytest.mark.parametrize(
    "arguments",
    [
        {"num_hierarchies": 3},
        {"codebook_size": 3},
        {"alignment_weight": -1},
        {"top_k_for_generation": 0},
        {"sequence_length": 2},
        {"sequence_length": 17},
        {"should_check_prefix": False},
    ],
)
def test_invalid_model_configuration_fails(arguments):
    with pytest.raises(ValueError):
        model(**arguments)


def test_default_history_budget_is_the_tiger_180_slot_information_budget():
    data = catalog([[0, 0, 0, 0], [0, 0, 0, 1]], 2)
    recommender = model(data, sequence_length=180)
    assert recommender.max_history == 44
    assert recommender.num_hierarchies == 4


@pytest.mark.parametrize(
    "ids,mask", [([[-1, -1]], [[0, 0]]), ([[0, -1, 1]], [[1, 0, 1]]), ([[4, -1]], [[1, 0]]), ([[0, 0]], [[1, 0]])]
)
def test_invalid_history_fails(ids, mask):
    with pytest.raises(ValueError):
        model().encode_history(TigerModelInput(input_ids=torch.tensor(ids), attention_mask=torch.tensor(mask)))
