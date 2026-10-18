"""磁盘暂存、唯一邻居 core、共同切分与原子发布。"""

import itertools
import json
import logging
import sqlite3
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from src.data.preparation.adapters import Amazon2014Adapter, SteamAdapter
from src.data.preparation.records import ShardWriter, file_hash, validate_sequence_splits

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreparationConfig:
    dataset: str
    source_dir: str
    output_dir: str
    protocol: str = "unique-neighbor-5core-loo-v1"
    items_file: str = "items.jsonl"
    interactions_file: str = "interactions.jsonl"
    user_core: int = 5
    item_core: int = 5
    deduplicate: bool = False
    user_stride: int = 1
    item_shards: int = 32
    sequence_shards: int = 128
    expected_world_size: int = 2
    expected_item_workers: int = 12
    expected_sequence_workers: int = 32

    def validate(self):
        for name in ("dataset", "source_dir", "output_dir", "protocol", "items_file", "interactions_file"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a nonempty string.")
        if self.dataset not in {"steam", "home_and_kitchen"}:
            raise ValueError("dataset must be steam or home_and_kitchen.")
        for name in (
            "user_core",
            "item_core",
            "user_stride",
            "item_shards",
            "sequence_shards",
            "expected_world_size",
            "expected_item_workers",
            "expected_sequence_workers",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        if self.user_core < 4:
            raise ValueError("user_core must be at least four for two holdouts and a training pair.")
        if not isinstance(self.deduplicate, bool):
            raise ValueError("deduplicate must be boolean.")
        if not self.protocol.strip():
            raise ValueError("protocol must be explicit.")
        if self.user_stride != 1 and (self.dataset != "steam" or self.protocol == "unique-neighbor-5core-loo-v1"):
            raise ValueError("Subsampling requires a distinct Steam protocol.")
        for name in ("items_file", "interactions_file"):
            value = Path(getattr(self, name))
            if value.is_absolute() or ".." in value.parts:
                raise ValueError("Source filenames must stay within source_dir.")
        source, output = Path(self.source_dir).resolve(), Path(self.output_dir).resolve()
        if output == source or source in output.parents or output in source.parents:
            raise ValueError("source_dir and output_dir must be separate, non-nested directories.")
        for shards, workers in (
            (self.item_shards, self.expected_item_workers),
            (self.sequence_shards, self.expected_sequence_workers),
        ):
            if shards < self.expected_world_size * workers:
                raise ValueError("Shard count must cover expected ranks times workers.")
        if not source.is_dir():
            raise FileNotFoundError(source)
        for name in (self.items_file, self.interactions_file):
            resolved = (source / name).resolve()
            if source not in resolved.parents:
                raise ValueError("Source file resolves outside source_dir.")
            if not (source / name).is_file():
                raise FileNotFoundError(source / name)


def _connect(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.executescript("""
        PRAGMA temp_store=FILE;
        PRAGMA cache_size=-65536;
        CREATE TABLE items(raw TEXT PRIMARY KEY, text TEXT NOT NULL, conflict INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE events(source_line INTEGER PRIMARY KEY, user TEXT NOT NULL, item TEXT NOT NULL, ts INTEGER NOT NULL);
    """)
    return db


def _ingest(db, adapter, limit):
    metadata_rows = 0
    for item in adapter.iter_items(limit):
        db.execute(
            """INSERT INTO items(raw,text) VALUES (?,?) ON CONFLICT(raw) DO UPDATE
                      SET conflict=items.conflict OR items.text != excluded.text""",
            (item.raw_id, item.text),
        )
        metadata_rows += 1
    events_read = 0
    for event in adapter.iter_interactions(limit):
        db.execute("INSERT INTO events VALUES (?,?,?,?)", (event.source_line, event.user, event.item, event.timestamp))
        events_read += 1
        if events_read % 100000 == 0:
            log.info("已读取 %s 条交互", events_read)
    db.commit()
    unknown = db.execute(
        "SELECT item FROM events WHERE NOT EXISTS (SELECT 1 FROM items WHERE raw=events.item) LIMIT 1"
    ).fetchone()
    if unknown:
        raise ValueError(f"Interaction item has no metadata in the consumed source: {unknown[0]}")
    db.execute("CREATE INDEX events_user_time ON events(user,ts,source_line)")
    return {
        "metadata_records_with_id": metadata_rows,
        "metadata_unique_ids": db.execute("SELECT COUNT(*) FROM items").fetchone()[0],
        "interactions_read": events_read,
        **dict(adapter.stats),
    }


def _filter(db, cfg):
    before = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if cfg.deduplicate:
        db.execute("""DELETE FROM events WHERE source_line IN (
            SELECT source_line FROM (SELECT source_line, ROW_NUMBER() OVER
            (PARTITION BY user,item ORDER BY ts,source_line) AS n FROM events) WHERE n>1)""")
    after_dedup = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    db.executescript("""CREATE TABLE edges AS SELECT DISTINCT user,item FROM events;
        CREATE UNIQUE INDEX edges_user_item ON edges(user,item);
        CREATE INDEX edges_item_user ON edges(item,user);""")
    iterations = 0
    while True:
        users = db.execute(
            "DELETE FROM edges WHERE user IN (SELECT user FROM edges GROUP BY user HAVING COUNT(*) < ?)",
            (cfg.user_core,),
        ).rowcount
        items = db.execute(
            "DELETE FROM edges WHERE item IN (SELECT item FROM edges GROUP BY item HAVING COUNT(*) < ?)",
            (cfg.item_core,),
        ).rowcount
        iterations += 1
        if not users and not items:
            break
    db.execute(
        "DELETE FROM events WHERE NOT EXISTS (SELECT 1 FROM edges x WHERE x.user=events.user AND x.item=events.item)"
    )
    core_events = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if not core_events:
        raise ValueError("Empty core: consumed records do not satisfy the configured unique-neighbor core.")
    db.execute("CREATE TABLE users(raw TEXT PRIMARY KEY, key INTEGER UNIQUE NOT NULL)")
    # stride7 定义为 BINARY 用户序中的第7、14……条；不复用 Python hash 或源机器时区。
    selected = (
        (raw, position)
        for position, (raw,) in enumerate(
            raw_row
            for index, raw_row in enumerate(db.execute("SELECT DISTINCT user FROM edges ORDER BY user COLLATE BINARY"))
            if index % cfg.user_stride == cfg.user_stride - 1
        )
    )
    db.executemany("INSERT INTO users VALUES (?,?)", selected)
    db.execute("DELETE FROM events WHERE user NOT IN (SELECT raw FROM users)")
    db.execute("CREATE TABLE item_map(raw TEXT PRIMARY KEY, key INTEGER UNIQUE NOT NULL)")
    db.executemany(
        "INSERT INTO item_map VALUES (?,?)",
        (
            (raw, key)
            for key, (raw,) in enumerate(db.execute("SELECT DISTINCT item FROM events ORDER BY item COLLATE BINARY"))
        ),
    )
    if not db.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        raise ValueError("Subsampling selected no users.")
    invalid = db.execute(
        "SELECT m.raw FROM item_map m JOIN items i ON i.raw=m.raw WHERE i.conflict OR i.text='' LIMIT 1"
    ).fetchone()
    if invalid:
        raise ValueError(f"Active item has conflicting or empty metadata content: {invalid[0]}")
    db.commit()
    return {
        "deduplicated_events": before - after_dedup,
        "core_events": core_events,
        "core_iterations": iterations,
        "final_interactions": db.execute("SELECT COUNT(*) FROM events").fetchone()[0],
    }


def _mapping(db, table, output):
    path = output / f"{'item' if table == 'item_map' else 'user'}_mapping.jsonl"
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for raw, key in db.execute(f"SELECT raw,key FROM {table} ORDER BY key"):
            handle.write(json.dumps({"raw_id": raw, "key": key}, ensure_ascii=False, separators=(",", ":")) + "\n")
            count += 1
    return {"path": path.name, "records": count, "sha256": file_hash(path)}


def _write(db, cfg, output):
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    item_count = db.execute("SELECT COUNT(*) FROM item_map").fetchone()[0]
    if user_count < cfg.sequence_shards or item_count < cfg.item_shards:
        raise ValueError(
            "Too few users/items for the configured nonempty shards; adjust explicit worker/shard settings."
        )
    writers = {}
    try:
        writers["items"] = ShardWriter(output / "items", cfg.item_shards)
        for key, text in db.execute("SELECT m.key,i.text FROM item_map m JOIN items i ON i.raw=m.raw ORDER BY m.key"):
            writers["items"].write({"id": [key], "text": text.encode("utf-8")})
        for split in ("training", "evaluation", "testing"):
            writers[split] = ShardWriter(output / split, cfg.sequence_shards)
        rows = db.execute("""SELECT u.key,m.key FROM events e JOIN users u ON e.user=u.raw
            JOIN item_map m ON e.item=m.raw ORDER BY u.key,e.ts,e.source_line""")
        seen = set()
        min_length, max_length = None, 0
        for user, group in itertools.groupby(rows, key=lambda row: row[0]):
            sequence = [item for _, item in group]
            if len(sequence) < 4 or any(not 0 <= item < item_count for item in sequence):
                raise ValueError("Invalid final sequence or catalog mapping.")
            min_length = min(min_length or len(sequence), len(sequence))
            max_length = max(max_length, len(sequence))
            seen.update(sequence[:-2])
            for split, values in (("training", sequence[:-2]), ("evaluation", sequence[:-1]), ("testing", sequence)):
                writers[split].write({"user_id": [user], "sequence_data": values})
        shards = {split: writer.finish() for split, writer in writers.items()}
        validate_sequence_splits(output, cfg.sequence_shards, user_count, item_count)
    finally:
        for writer in writers.values():
            writer.close()
    return shards, {
        "users": user_count,
        "items": item_count,
        "training_seen_items": len(seen),
        "cold_items": item_count - len(seen),
        "min_sequence_events": min_length,
        "max_sequence_events": max_length,
    }


def _build(cfg, output, limit):
    adapter_cls = SteamAdapter if cfg.dataset == "steam" else Amazon2014Adapter
    adapter = adapter_cls(Path(cfg.source_dir), cfg.items_file, cfg.interactions_file)
    work = output / "work.sqlite"
    db = _connect(work)
    try:
        stats = _ingest(db, adapter, limit)
        stats.update(_filter(db, cfg))
        mappings = {name: _mapping(db, table, output) for name, table in (("users", "users"), ("items", "item_map"))}
        shards, counts = _write(db, cfg, output)
    finally:
        db.close()
    work.unlink()
    code_files = sorted(Path(__file__).parent.glob("*.py"))
    manifest = {
        "schema_version": "grid-prepared-dataset-v1",
        "dataset": cfg.dataset,
        "protocol": cfg.protocol,
        "scope": "bounded_dry_run" if limit else "full",
        "record_limit_per_source": limit,
        "config": asdict(cfg),
        "sources": adapter.sources,
        "code_sha256": {path.name: file_hash(path) for path in code_files},
        "rules": {
            "core": "unique_neighbors_iterative",
            "duplicates": "earliest_event" if cfg.deduplicate else "preserved",
            "order": ["timestamp_utc", "source_line"],
            "split": "leave_last_two_events",
            "mapping": "raw_id_binary_sorted_zero_based",
            "history_truncation": False,
            "subsample": {
                "stride": cfg.user_stride,
                "phase": "after_core",
                "order": "raw_user_id_binary",
                "offset": cfg.user_stride - 1,
                "recore": False,
                "paper_exact_reproduction": False,
            },
        },
        "processing": stats,
        "counts": counts,
        "mappings": mappings,
        "shards": shards,
        "validation": "all_shards_readback_equal_to_expected_rows",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def prepare_dataset(config: PreparationConfig, *, dry_run: bool = False, max_records: int = 500000) -> dict:
    """完整准备发布新目录；dry-run 在系统临时目录执行同流程且不发布正式产物。"""
    config.validate()
    if isinstance(max_records, bool) or not isinstance(max_records, int) or max_records < 1:
        raise ValueError("max_records must be a positive integer.")
    destination = Path(config.output_dir).resolve()
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite prepared dataset: {destination}")
    if dry_run:
        with tempfile.TemporaryDirectory(prefix="grid-data-dry-run-") as directory:
            return _build(config, Path(directory), max_records)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # 与目标同一文件系统，成功后只做目录 rename；失败不会发布半成品。
    with tempfile.TemporaryDirectory(prefix=f".{destination.name}-", dir=destination.parent) as directory:
        output = Path(directory) / "dataset"
        output.mkdir()
        manifest = _build(config, output, None)
        if destination.exists():
            raise FileExistsError(destination)
        output.rename(destination)
    return manifest
