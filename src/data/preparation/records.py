"""确定性 gzip TFRecord Example 写出和原有 reader 回读校验。"""

import gzip
import hashlib
import json
import shutil
from itertools import zip_longest
from pathlib import Path

from tfrecord import example_pb2
from tfrecord.writer import TFRecordWriter

from src.data.components.readers import TFRecordReader


def validate_sequence_splits(directory: Path, shards: int, users: int, items: int):
    """按对应分片逐用户核对身份、留出前缀及目录覆盖。"""
    count = 0
    for index in range(shards):
        streams = [
            TFRecordReader([str(directory / split / f"part-{index:05d}.tfrecord.gz")]).iterrows()
            for split in ("training", "evaluation", "testing")
        ]
        for position, rows in enumerate(zip_longest(*streams)):
            if any(row is None for row in rows):
                raise ValueError("Split row counts differ.")
            expected = index + position * shards
            keys = [row["user_id"].reshape(-1).tolist() for row in rows]
            train, val, test = [row["sequence_data"].reshape(-1).tolist() for row in rows]
            if keys != [[expected]] * 3 or len(train) < 2 or train != val[:-1] or val != test[:-1]:
                raise ValueError("Split user identity or holdout prefix mismatch.")
            if any(not 0 <= item < items for item in test):
                raise ValueError("Split contains an unknown catalog key.")
            count += 1
    if count != users:
        raise ValueError("Split users do not match the mapping.")


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def row_hash(row: dict) -> bytes:
    # 忽略 protobuf 字段顺序，按消费方可见的字段和值比较。
    normalized = {}
    for key, value in row.items():
        if isinstance(value, bytes):
            normalized[key] = value.decode("utf-8")
        else:
            normalized[key] = [int(v) for v in value]
    return (json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


class _DeterministicWriter(TFRecordWriter):
    @staticmethod
    def serialize_tf_example(datum):
        message = example_pb2.Example.FromString(TFRecordWriter.serialize_tf_example(datum))
        return message.SerializeToString(deterministic=True)


class ShardWriter:
    def __init__(self, directory: Path, shards: int):
        directory.mkdir()
        self.paths = [directory / f"part-{index:05d}.tfrecord" for index in range(shards)]
        self.writers = [_DeterministicWriter(str(path)) for path in self.paths]
        self.counts = [0] * shards
        self.digests = [hashlib.sha256() for _ in self.paths]
        self.rows = 0

    def write(self, row: dict):
        index = self.rows % len(self.writers)
        datum = {key: (value, "byte" if isinstance(value, bytes) else "int") for key, value in row.items()}
        self.writers[index].write(datum)
        self.digests[index].update(row_hash(row))
        self.counts[index] += 1
        self.rows += 1

    def close(self):
        for writer in self.writers:
            writer.close()

    def finish(self) -> list[dict]:
        self.close()
        if not all(self.counts):
            raise ValueError("Not enough rows for nonempty shards; lower shard/worker counts explicitly.")
        result = []
        for path, count, expected in zip(self.paths, self.counts, self.digests, strict=True):
            compressed = path.with_suffix(".tfrecord.gz")
            with path.open("rb") as inp, compressed.open("xb") as out:
                with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as stream:
                    shutil.copyfileobj(inp, stream)
            actual = hashlib.sha256()
            actual_count = 0
            for row in TFRecordReader([str(compressed)]).iterrows():
                actual.update(row_hash(row))
                actual_count += 1
            if actual_count != count or actual.digest() != expected.digest():
                raise ValueError(f"TFRecord readback mismatch: {compressed}")
            path.unlink()
            result.append(
                {
                    "path": f"{path.parent.name}/{compressed.name}",
                    "records": count,
                    "bytes": compressed.stat().st_size,
                    "sha256": file_hash(compressed),
                    "row_sha256": actual.hexdigest(),
                }
            )
        return result
