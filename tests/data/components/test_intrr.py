import pytest
import torch

from src.data.components.collate import collate_fn_sequence
from src.data.components.data_models import ModelOutput, TigerLabelData, TigerModelInput
from src.data.components.intrr import CompressTigerHistory, IntrrCatalog, intrr_collate, load_intrr_catalog
from src.data.components.preprocessing import (
    expand_sid_causal_duplicate_sequences,
    generate_next_k_labels,
    map_sparse_id_to_semantic_id,
    normalize_sequence,
)


def catalog_and_bundle(count=80):
    keys = torch.arange(count) * 3
    sids = torch.stack((torch.arange(count), torch.zeros(count), torch.zeros(count), torch.zeros(count)), -1).long()
    bundle = ModelOutput(keys=keys, predictions=sids)
    return IntrrCatalog(keys, sids), bundle


def tiger_rows(raw, bundle, *, training=False, seed=42):
    torch.manual_seed(seed)
    mapped = map_sparse_id_to_semantic_id(
        {key: value.clone() for key, value in raw.items()}, bundle, ["sequence_data"], num_hierarchies=4
    )
    rows = (
        expand_sid_causal_duplicate_sequences(mapped, "sequence_data", 4, max_num_sequences=32)
        if training
        else [mapped]
    )
    return [
        normalize_sequence(
            generate_next_k_labels(row, "sequence_data", next_k=4, masking_token=0, padding_token=-1),
            sequence_length=180,
            sid_hierarchy=4,
            padding_token=-1,
        )
        for row in rows
    ]


@pytest.mark.parametrize("count", [6, 70])
def test_same_seed_training_samples_history_and_targets_match_tiger(count):
    catalog, bundle = catalog_and_bundle()
    raw = {"sequence_data": bundle.keys[:count]}
    original = tiger_rows(raw, bundle, training=True, seed=200)
    adapted = [CompressTigerHistory(catalog)(row) for row in tiger_rows(raw, bundle, training=True, seed=200)]
    assert 0 < len(original) == len(adapted) <= 32
    for tiger, intrr in zip(original, adapted, strict=True):
        assert torch.equal(tiger["target_ids"], intrr["target_ids"])
        groups = tiger["input_ids"].reshape(-1, 4)
        expected_history = groups[groups.ge(0).all(dim=-1)]
        uids = intrr["input_ids"][intrr["attention_mask"].bool()]
        assert torch.equal(catalog.semantic_ids[uids], expected_history)
        assert intrr["input_ids"].shape == (44,)
        assert intrr["input_ids"][len(uids) :].eq(-1).all()
    model_input, labels = collate_fn_sequence(adapted)
    assert isinstance(model_input, TigerModelInput) and isinstance(labels, TigerLabelData)
    assert model_input.output_keys is None and model_input.input_ids.shape == (len(adapted), 44)


def test_long_evaluation_uses_same_last_44_items_and_preserves_user():
    catalog, bundle = catalog_and_bundle()
    raw = {"sequence_data": bundle.keys[:70], "user_id": torch.tensor(321)}
    tiger = tiger_rows(raw, bundle)[0]
    intrr = CompressTigerHistory(catalog)(tiger)
    assert intrr["input_ids"].tolist() == list(range(25, 69))
    assert intrr["target_ids"].tolist() == bundle.predictions[69].tolist()
    assert torch.equal(tiger["input_ids"].reshape(-1, 4)[-1], torch.tensor([0, -1, -1, -1]))
    model_input, labels = collate_fn_sequence([intrr], output_key_field_name="user_id")
    assert model_input.output_keys.tolist() == [321]
    assert labels.target_ids.tolist() == [bundle.predictions[69].tolist()]


def test_zero_codes_are_history_and_short_sequence_right_padding_is_exact():
    catalog, bundle = catalog_and_bundle()
    tiger = tiger_rows({"sequence_data": bundle.keys[:3]}, bundle)[0]
    original_inputs = tiger["input_ids"].clone()
    intrr = CompressTigerHistory(catalog)(tiger)
    assert intrr["input_ids"][:2].tolist() == [0, 1]
    assert intrr["input_ids"][2:].eq(-1).all()
    assert intrr["attention_mask"].tolist() == [1, 1] + [0] * 42
    assert torch.equal(tiger["input_ids"], original_inputs)


@pytest.mark.parametrize("inference", [False, True])
def test_collate_wrapper_reuses_public_containers_and_preserves_optional_user_key(inference):
    catalog, bundle = catalog_and_bundle()
    raw = {"sequence_data": bundle.keys[:5]}
    if inference:
        raw["user_id"] = torch.tensor(27)
    rows = tiger_rows(raw, bundle, training=not inference)
    model_input, label = intrr_collate(
        rows,
        catalog,
        input_field_name="input_ids",
        attention_mask_field_name="attention_mask",
        target_field_name="target_ids",
        output_key_field_name="user_id" if inference else None,
    )
    assert isinstance(model_input, TigerModelInput) and isinstance(label, TigerLabelData)
    assert model_input.input_ids.shape == (len(rows), 44)
    assert torch.equal(label.target_ids, torch.stack([row["target_ids"] for row in rows]))
    assert (model_input.output_keys.tolist() == [27]) if inference else model_input.output_keys is None


def test_catalog_key_order_and_identity_are_stable_and_loader_uses_bundle(tmp_path):
    catalog, bundle = catalog_and_bundle(3)
    reverse = torch.tensor([2, 0, 1])
    reordered = IntrrCatalog(bundle.keys[reverse], bundle.predictions[reverse])
    assert torch.equal(reordered.keys, catalog.keys)
    assert torch.equal(reordered.semantic_ids, catalog.semantic_ids)
    assert reordered.sha256 == catalog.sha256
    path = tmp_path / "sid.pt"
    torch.save({"keys": bundle.keys[reverse], "predictions": bundle.predictions[reverse]}, path)
    loaded = load_intrr_catalog(str(path))
    assert loaded.sha256 == catalog.sha256
    assert loaded.uids_from_semantic_ids(bundle.predictions[reverse]).tolist() == reverse.tolist()
    assert IntrrCatalog(bundle.keys + 1, bundle.predictions).sha256 != catalog.sha256
    assert IntrrCatalog(bundle.keys, bundle.predictions, codebook_size=255).sha256 != catalog.sha256


def test_catalog_selects_first_hierarchies_and_rejects_collisions_even_with_unique_extra_column():
    sids = torch.tensor([[0, 1, 0, 0, 4], [1, 0, 0, 0, 5]])
    catalog = IntrrCatalog(torch.tensor([0, 8]), sids)
    assert catalog.semantic_ids.shape == (2, 4)
    sids[1, :4] = sids[0, :4]
    with pytest.raises(ValueError, match="unique SIDs"):
        IntrrCatalog(torch.tensor([0, 8]), sids)


@pytest.mark.parametrize(
    ("keys", "sids", "kwargs", "match"),
    [
        ([], torch.empty(0, 4, dtype=torch.long), {}, "nonempty"),
        ([0.0], [[0, 0, 0, 0]], {}, "integer item keys"),
        ([0, 0], [[0, 0, 0, 0], [1, 1, 1, 1]], {}, "unique and nonnegative"),
        ([-1], [[0, 0, 0, 0]], {}, "unique and nonnegative"),
        ([0], [[0, 0, 0]], {}, "integer SID matrix"),
        ([0], [[0.0, 0, 0, 0]], {}, "integer SID matrix"),
        ([0], [[0, 0, 0, -1]], {}, "outside codebook"),
        ([0], [[0, 0, 0, 256]], {}, "outside codebook"),
        ([0], [[0, 0, 0, 0]], {"num_hierarchies": 0}, "positive integer"),
        ([0], [[0, 0, 0, 0]], {"codebook_size": 0}, "positive integer"),
    ],
)
def test_invalid_catalog_fails(keys, sids, kwargs, match):
    with pytest.raises(ValueError, match=match):
        IntrrCatalog(keys, sids, **kwargs)


@pytest.mark.parametrize("sequence_length", [0, 4, 179, 181, 180.0])
def test_invalid_normalized_length_fails(sequence_length):
    catalog, _ = catalog_and_bundle(3)
    with pytest.raises(ValueError, match="complete SID groups"):
        CompressTigerHistory(catalog, sequence_length)


@pytest.mark.parametrize("failure", ["partial", "unknown", "placeholder", "padding_gap", "mask", "target"])
def test_bad_normalized_rows_fail(failure):
    catalog, bundle = catalog_and_bundle(3)
    row = tiger_rows({"sequence_data": bundle.keys[:3]}, bundle)[0]
    if failure == "partial":
        row["input_ids"][1] = -1
    elif failure == "unknown":
        row["input_ids"][0] = 255
    elif failure == "placeholder":
        row["input_ids"][8] = 1
    elif failure == "padding_gap":
        row["input_ids"][:4] = -1
    elif failure == "mask":
        row["attention_mask"][0] = 0
    else:
        row["target_ids"][0] = 255
    if failure != "mask":
        row["attention_mask"] = row["input_ids"].ne(-1).long()
    with pytest.raises(ValueError):
        CompressTigerHistory(catalog)(row)
