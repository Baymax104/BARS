"""来源适配器只处理身份、时间和商品内容，不执行模型预处理。"""

import hashlib
import html
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class Item:
    raw_id: str
    text: str


@dataclass(frozen=True)
class Interaction:
    user: str
    item: str
    timestamp: int
    source_line: int


def identity(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Source identity must be a nonempty string.")
    return value


def clean(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(part for entry in value if (part := clean(entry)))
    if isinstance(value, dict) or isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Invalid content attribute.")
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", str(value))).split())


class SourceAdapter:
    item_field = ""
    user_field = ""
    interaction_item_field = ""
    content_fields: tuple[str, ...] = ()

    def __init__(self, source_dir: Path, items_file: str, interactions_file: str):
        self.paths = {"items": source_dir / items_file, "interactions": source_dir / interactions_file}
        self.sources: dict[str, dict] = {}
        self.stats: Counter = Counter()

    def _rows(self, kind: str, limit: int | None):
        path = self.paths[kind]
        before = path.stat()
        digest = hashlib.sha256()
        consumed = records = line_number = 0
        with path.open("rb") as handle:
            while limit is None or records < limit:
                line = handle.readline()
                if not line:
                    break
                line_number += 1
                consumed += len(line)
                digest.update(line)
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError("JSONL record must be an object.")
                except (ValueError, UnicodeError) as error:
                    raise ValueError(f"{path}:{line_number}: {error}") from error
                records += 1
                yield line_number, row
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError(f"Source changed while reading: {path}")
        self.sources[kind] = {
            "path": str(path.resolve()),
            "file_bytes": before.st_size,
            "records_read": records,
            "bytes_read": consumed,
            "sha256": digest.hexdigest(),
            "hash_scope": "full_file" if consumed == before.st_size else "prefix",
        }

    def iter_items(self, limit: int | None = None):
        for line_number, row in self._rows("items", limit):
            if row.get(self.item_field) in (None, ""):
                self.stats["metadata_without_id"] += 1
                continue
            try:
                item = identity(row[self.item_field])
                values = {field: clean(row.get(field)) for field in self.content_fields}
                if self.item_field == "id" and not values.get("title"):
                    values["title"] = clean(row.get("app_name"))
                text = "\n".join(f"{field}: {value}" for field, value in values.items() if value)
                yield Item(item, text)
            except (KeyError, ValueError) as error:
                raise ValueError(f"{self.paths['items']}:{line_number}: {error}") from error

    def timestamp(self, row: dict) -> int:
        raise NotImplementedError

    def iter_interactions(self, limit: int | None = None):
        for line_number, row in self._rows("interactions", limit):
            try:
                yield Interaction(
                    identity(row[self.user_field]),
                    identity(row[self.interaction_item_field]),
                    self.timestamp(row),
                    line_number,
                )
            except (KeyError, ValueError, TypeError, OverflowError) as error:
                raise ValueError(f"{self.paths['interactions']}:{line_number}: {error}") from error


class SteamAdapter(SourceAdapter):
    item_field = "id"
    user_field = "username"
    interaction_item_field = "product_id"
    content_fields = ("title", "genres", "specs", "tags", "price", "publisher")

    def timestamp(self, row: dict) -> int:
        value = datetime.fromisoformat(row["date"])
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return int(value.timestamp())


class Amazon2014Adapter(SourceAdapter):
    item_field = "asin"
    user_field = "reviewerID"
    interaction_item_field = "asin"
    content_fields = ("title", "categories", "description", "brand", "price")

    def timestamp(self, row: dict) -> int:
        value = row["unixReviewTime"]
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("unixReviewTime must be an integer UTC timestamp.")
        return value
