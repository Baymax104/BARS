import json
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
import torch

from src.data.components.collate import collate_fn_items, collate_fn_sasrec, collate_fn_sequence
from src.data.components.data_models import ItemBatch, ModelOutput, SASRecModelInput, TigerModelInput
from src.data.components.letter import LetterCatalog, LetterPreprocessor, letter_collate
from src.data.components.letter_cf import LetterCFCatalog, LetterCFPreprocessor, letter_cf_collate
from src.data.components.liger import generate_liger_next_item
from src.data.components.preprocessing import (
    generate_next_k_labels,
    map_sparse_id_to_embedding,
    map_sparse_id_to_semantic_id,
    normalize_sequence,
)
from src.data.components.readers import TFRecordReader
from src.data.components.sasrec import ItemCatalog, SASRecPreprocessor
from src.data.preparation import PreparationConfig, prepare_dataset
from src.data.preparation.__main__ import load_config, main
from src.data.preparation.adapters import SteamAdapter
from src.data.preparation.records import ShardWriter, validate_sequence_splits

ROOT = Path(__file__).resolve().parents[3]


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def make_source(tmp_path, dataset="steam"):
    source = tmp_path / "source with spaces"
    source.mkdir()
    items, events = [], []
    for index in reversed(range(7)):
        row = {"title": f"<b>商品 &amp; {index}</b>", "price": "Free" if dataset == "steam" else 1.0}
        row["id" if dataset == "steam" else "asin"] = f"i{index:02d}"
        items.append(row)
    # 同 ID 内容一致但 URL 不同可合并，无 ID metadata 原样来源计数但不进目录。
    items += [dict(items[0], url="different"), {"title": "missing id"}]
    for user in reversed(range(6)):
        sequence = [(5, 5), (0, 0), (2, 1), (1, 1), (2, 2), (3, 3), (4, 4)] if user == 0 else [(i, i) for i in range(6)]
        for item, day in sequence:
            if dataset == "steam":
                events.append(
                    {
                        "username": f"u{user:02d}",
                        "product_id": f"i{item:02d}",
                        "date": str(date(2020, 1, 1) + timedelta(days=day)),
                        "text": "DO_NOT_EMBED_REVIEW",
                    }
                )
            else:
                events.append(
                    {
                        "reviewerID": f"u{user:02d}",
                        "asin": f"i{item:02d}",
                        "unixReviewTime": int(datetime(2020, 1, 1, tzinfo=UTC).timestamp()) + day * 86400,
                        "reviewText": "DO_NOT_EMBED_REVIEW",
                    }
                )
    write_jsonl(source / "items.jsonl", items)
    write_jsonl(source / "interactions.jsonl", events)
    return PreparationConfig(
        dataset,
        str(source),
        str(tmp_path / "prepared"),
        item_shards=2,
        sequence_shards=2,
        expected_world_size=2,
        expected_item_workers=1,
        expected_sequence_workers=1,
    )


def read_rows(output, split):
    rows = list(TFRecordReader([str(p) for p in sorted((output / split).glob("*.tfrecord.gz"))]).iterrows())
    key = "id" if split == "items" else "user_id"
    return sorted(rows, key=lambda row: int(row[key][0]))


@pytest.mark.parametrize("dataset", ["steam", "home_and_kitchen"])
def test_prepare_contract_and_reproducibility(tmp_path, dataset):
    cfg = make_source(tmp_path, dataset)
    first = prepare_dataset(cfg)
    output = Path(cfg.output_dir)
    assert first["counts"] == {
        "users": 6,
        "items": 6,
        "training_seen_items": 4,
        "cold_items": 2,
        "min_sequence_events": 6,
        "max_sequence_events": 7,
    }
    assert first["processing"]["final_interactions"] == 37
    assert first["processing"]["metadata_without_id"] == 1
    mapping = [json.loads(line) for line in (output / "item_mapping.jsonl").read_text(encoding="utf-8").splitlines()]
    assert mapping == [{"raw_id": f"i{i:02d}", "key": i} for i in range(6)]
    items = read_rows(output, "items")
    assert items[0]["id"].tolist() == [0]
    assert "商品 & 0" in items[0]["text"].decode()
    assert all(set(row) == {"id", "text"} and b"DO_NOT_EMBED_REVIEW" not in row["text"] for row in items)
    splits = {split: read_rows(output, split) for split in ("training", "evaluation", "testing")}
    assert splits["testing"][0]["sequence_data"].tolist() == [0, 2, 1, 2, 3, 4, 5]
    for train, val, test in zip(*splits.values(), strict=True):
        assert train["user_id"].tolist() == val["user_id"].tolist() == test["user_id"].tolist()
        assert train["sequence_data"].tolist() == val["sequence_data"][:-1].tolist()
        assert val["sequence_data"].tolist() == test["sequence_data"][:-1].tolist()
    second = prepare_dataset(replace(cfg, output_dir=str(tmp_path / "second")))
    assert first["shards"] == second["shards"] and first["mappings"] == second["mappings"]
    with pytest.raises(FileExistsError):
        prepare_dataset(cfg)
    assert not list(output.glob("*.sqlite"))


def test_core_uses_unique_neighbors_and_cascades(tmp_path):
    cfg = make_source(tmp_path)
    source = Path(cfg.source_dir)
    events = [json.loads(line) for line in (source / "interactions.jsonl").read_text().splitlines()]
    events += [{"username": "weak", "product_id": "i06", "date": "2020-01-01"} for _ in range(9)]
    # 该用户初始有5个邻居；i06被剔除后仅剩4个，必须在下一轮移除。
    events += [{"username": "cascade", "product_id": f"i{i:02d}", "date": "2020-01-01"} for i in (0, 1, 2, 3, 6)]
    write_jsonl(source / "interactions.jsonl", events)
    report = prepare_dataset(cfg)
    assert report["counts"]["users"] == 6
    assert report["processing"]["final_interactions"] == 37
    assert report["processing"]["core_iterations"] >= 3


def test_explicit_dedup_and_stride_profiles(tmp_path):
    cfg = make_source(tmp_path)
    report = prepare_dataset(replace(cfg, deduplicate=True))
    assert report["processing"]["deduplicated_events"] == 1
    assert read_rows(Path(cfg.output_dir), "testing")[0]["sequence_data"].tolist() == [0, 2, 1, 3, 4, 5]
    subset = replace(cfg, output_dir=str(tmp_path / "subset"), protocol="steam-stride2-v1", user_stride=2)
    report = prepare_dataset(subset)
    users = [
        json.loads(line)["raw_id"] for line in (Path(subset.output_dir) / "user_mapping.jsonl").read_text().splitlines()
    ]
    assert users == ["u01", "u03", "u05"]
    assert report["rules"]["subsample"]["recore"] is False


def test_dry_run_bounded_no_publication_and_empty_core_failure(tmp_path):
    cfg = make_source(tmp_path)
    before = {p.name: p.read_bytes() for p in Path(cfg.source_dir).iterdir()}
    report = prepare_dataset(cfg, dry_run=True, max_records=35)
    assert report["scope"] == "bounded_dry_run"
    assert report["sources"]["interactions"]["records_read"] == 35
    assert report["sources"]["interactions"]["hash_scope"] == "prefix"
    assert not Path(cfg.output_dir).exists()
    with pytest.raises(ValueError, match="Empty core"):
        prepare_dataset(cfg, dry_run=True, max_records=10)
    assert not Path(cfg.output_dir).exists()
    assert before == {p.name: p.read_bytes() for p in Path(cfg.source_dir).iterdir()}


@pytest.mark.parametrize("kind", ["unknown", "conflict", "empty", "bad_date", "bad_json"])
def test_invalid_source_fails_without_publishing(tmp_path, kind):
    cfg = make_source(tmp_path)
    source = Path(cfg.source_dir)
    if kind in ("conflict", "empty"):
        items = [json.loads(line) for line in (source / "items.jsonl").read_text().splitlines()]
        if kind == "conflict":
            items.append({"id": "i00", "title": "different content"})
        else:
            items = [({"id": "i00"} if row.get("id") == "i00" else row) for row in items]
        write_jsonl(source / "items.jsonl", items)
    else:
        events = [json.loads(line) for line in (source / "interactions.jsonl").read_text().splitlines()]
        if kind == "unknown":
            events[0]["product_id"] = "unknown"
        elif kind == "bad_date":
            events[0]["date"] = "invalid"
        write_jsonl(source / "interactions.jsonl", events)
        if kind == "bad_json":
            with (source / "interactions.jsonl").open("a") as handle:
                handle.write("not JSON\n")
    with pytest.raises(ValueError):
        prepare_dataset(cfg)
    assert not Path(cfg.output_dir).exists()


def test_existing_preprocessors_and_collates_unchanged(tmp_path):
    cfg = make_source(tmp_path)
    prepare_dataset(cfg)
    row = read_rows(Path(cfg.output_dir), "testing")[0]
    catalog = ItemCatalog(torch.arange(6))
    x, labels = collate_fn_sasrec([SASRecPreprocessor(catalog)(row)])
    assert isinstance(x, SASRecModelInput) and x.output_keys.tolist() == [0]
    assert labels.target_ids.tolist() == [6]
    codes = torch.tensor([[i, 0, 0, 0] for i in range(6)])
    bundle = ModelOutput(keys=torch.arange(6), predictions=codes)
    semantic = map_sparse_id_to_semantic_id(
        {"sequence_data": torch.tensor(row["sequence_data"]), "user_id": torch.tensor(row["user_id"])},
        bundle,
        ["sequence_data"],
        4,
    )
    for label_fn in (generate_next_k_labels, generate_liger_next_item):
        labeled = label_fn(dict(semantic), sequence_field_name="sequence_data", next_k=4)
        normalized = normalize_sequence(labeled, sequence_length=80, sid_hierarchy=4, padding_token=-1)
        x, labels = collate_fn_sequence([normalized], output_key_field_name="user_id")
        assert isinstance(x, TigerModelInput) and x.input_ids.shape == (1, 80)
        assert x.output_keys.tolist() == [0] and labels.target_ids.shape == (1, 4)
    letter = LetterPreprocessor(LetterCatalog(torch.arange(6), codes))({**row})
    batch = letter_collate(letter)
    assert batch["target"].tolist() == [5] and batch["user_id"].tolist() == [0]
    cf = LetterCFPreprocessor(LetterCFCatalog(torch.arange(10)))(row)
    assert letter_cf_collate([cf])["target"].tolist() == [5]
    item = read_rows(Path(cfg.output_dir), "items")[0]
    embeddings = ModelOutput(keys=torch.arange(6), predictions=torch.ones(6, 1024))
    prepared = map_sparse_id_to_embedding({"id": torch.tensor(item["id"])}, embeddings)
    batch = collate_fn_items([prepared], "id", {"embedding": "input_embedding"})
    assert isinstance(batch, ItemBatch) and batch.item_ids.tolist() == [[0]]
    assert batch.features["input_embedding"].shape == (1, 1024)


def test_readback_detects_misaligned_split(tmp_path):
    for split, sequence in (("training", [0, 1]), ("evaluation", [0, 1, 2]), ("testing", [0, 3, 2, 1])):
        writer = ShardWriter(tmp_path / split, 1)
        writer.write({"user_id": [0], "sequence_data": sequence})
        writer.finish()
    with pytest.raises(ValueError, match="prefix"):
        validate_sequence_splits(tmp_path, 1, 1, 4)


def test_profiles_and_cli_report(tmp_path, capsys):
    cfg = make_source(tmp_path)
    profile = str(ROOT / "configs/data_preparation/steam_full.yaml")
    for path in (ROOT / "configs/data_preparation").glob("*.yaml"):
        loaded = load_config(str(path), [])
        assert loaded.user_core == loaded.item_core == 5 and not loaded.deduplicate
        assert loaded.item_shards >= loaded.expected_world_size * loaded.expected_item_workers
    overrides = [
        f"source_dir={cfg.source_dir}",
        f"output_dir={cfg.output_dir}",
        "item_shards=2",
        "sequence_shards=2",
        "expected_item_workers=1",
        "expected_sequence_workers=1",
    ]
    report = tmp_path / "receipt.json"
    main(["--config", profile, "--dry-run", "--max-records", "100", "--report", str(report), *overrides])
    assert json.loads(report.read_text(encoding="utf-8"))["scope"] == "bounded_dry_run"
    assert json.loads(capsys.readouterr().out)["counts"]["users"] == 6
    assert not Path(cfg.output_dir).exists()
    with pytest.raises(SystemExit) as error:
        main(["--config", profile, "unknown=1"])
    assert error.value.code == 2
    with pytest.raises(ValueError):
        replace(cfg, item_shards=1).validate()
    with pytest.raises(ValueError):
        replace(cfg, output_dir=cfg.source_dir).validate()


def test_adapter_utc_and_title_fallback(tmp_path):
    cfg = make_source(tmp_path)
    source = Path(cfg.source_dir)
    write_jsonl(source / "items.jsonl", [{"id": "0001", "app_name": "Fallback", "price": "Free"}])
    adapter = SteamAdapter(source, "items.jsonl", "interactions.jsonl")
    assert list(adapter.iter_items())[0].text == "title: Fallback\nprice: Free"
    assert adapter.timestamp({"date": "1970-01-01"}) == 0
    assert adapter.timestamp({"date": "1970-01-01T01:00:00+01:00"}) == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_dir", ""),
        ("output_dir", ""),
        ("protocol", None),
        ("user_core", True),
        ("item_core", 0),
        ("items_file", "../items.jsonl"),
        ("deduplicate", "false"),
        ("user_stride", 7),
    ],
)
def test_config_rejects_invalid_or_ambiguous_values(tmp_path, field, value):
    cfg = make_source(tmp_path)
    with pytest.raises(ValueError):
        replace(cfg, **{field: value}).validate()
