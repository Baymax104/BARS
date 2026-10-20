"""IntRR 商品目录与 TIGER 预处理末端的表示压缩适配。"""

import hashlib

import torch

from src.data.components.artifacts import load_model_output
from src.data.components.collate import collate_fn_sequence


class IntrrCatalog:
    """按原始 key 排序建立 compact UID，固定 SID 与 UID 的双向身份。"""

    def __init__(self, keys, semantic_ids, num_hierarchies=4, codebook_size=256):
        if not isinstance(num_hierarchies, int) or num_hierarchies < 1:
            raise ValueError("IntRR num_hierarchies must be a positive integer.")
        if not isinstance(codebook_size, int) or codebook_size < 1:
            raise ValueError("IntRR codebook_size must be a positive integer.")
        keys, semantic_ids = torch.as_tensor(keys), torch.as_tensor(semantic_ids)
        if keys.ndim != 1 or keys.dtype not in (torch.int32, torch.int64) or not len(keys):
            raise ValueError("IntRR requires nonempty integer item keys.")
        if keys.unique().numel() != len(keys) or (keys < 0).any():
            raise ValueError("IntRR item keys must be unique and nonnegative.")
        if (
            semantic_ids.ndim != 2
            or semantic_ids.shape[0] != len(keys)
            or semantic_ids.shape[1] < num_hierarchies
            or semantic_ids.dtype not in (torch.int32, torch.int64)
        ):
            raise ValueError("IntRR requires an integer SID matrix with at least num_hierarchies columns.")
        semantic_ids = semantic_ids[:, :num_hierarchies]
        if (semantic_ids < 0).any() or (semantic_ids >= codebook_size).any():
            raise ValueError("IntRR SID code outside codebook.")
        if semantic_ids.unique(dim=0).shape[0] != len(keys):
            raise ValueError("IntRR requires unique SIDs in the selected num_hierarchies columns.")
        order = keys.argsort()
        self.keys = keys[order].detach().cpu().long().contiguous()
        self.semantic_ids = semantic_ids[order].detach().cpu().long().contiguous()
        self.num_hierarchies, self.codebook_size = num_hierarchies, codebook_size
        self._uid_by_sid = {tuple(sid): uid for uid, sid in enumerate(self.semantic_ids.tolist())}
        identity = torch.tensor([num_hierarchies, codebook_size], dtype=torch.long)
        self.sha256 = hashlib.sha256(
            self.keys.numpy().astype("<i8").tobytes()
            + self.semantic_ids.numpy().astype("<i8").tobytes()
            + identity.numpy().astype("<i8").tobytes()
        ).hexdigest()

    def uids_from_semantic_ids(self, semantic_ids):
        """只在数据适配时查表；未知 SID 明确失败，padding 不进入目录。"""
        semantic_ids = torch.as_tensor(semantic_ids)
        if (
            semantic_ids.ndim != 2
            or semantic_ids.shape[1] != self.num_hierarchies
            or semantic_ids.dtype not in (torch.int32, torch.int64)
        ):
            raise ValueError("IntRR SID lookup requires an integer [items, num_hierarchies] matrix.")
        try:
            uids = [self._uid_by_sid[tuple(sid)] for sid in semantic_ids.detach().cpu().tolist()]
        except KeyError as error:
            raise ValueError("History or target contains an SID absent from the IntRR catalog.") from error
        return torch.tensor(uids, dtype=torch.long)


def load_intrr_catalog(
    semantic_id_path, num_hierarchies=4, codebook_size=256, wandb_entity=None, wandb_project=None
):
    bundle = load_model_output(
        semantic_id_path, field_name="semantic_id_path", wandb_entity=wandb_entity, wandb_project=wandb_project
    )
    return IntrrCatalog(bundle.keys, bundle.predictions, num_hierarchies, codebook_size)


class CompressTigerHistory:
    """保留 TIGER 样本和截断结果，仅将完整历史商品 SID 压为 compact UID。"""

    def __init__(self, catalog, sequence_length=180):
        if (
            not isinstance(sequence_length, int)
            or sequence_length < 2 * catalog.num_hierarchies
            or sequence_length % catalog.num_hierarchies
        ):
            raise ValueError("IntRR sequence_length must contain at least two complete SID groups.")
        self.catalog, self.sequence_length = catalog, sequence_length
        self.max_history_items = sequence_length // catalog.num_hierarchies - 1

    def __call__(self, row):
        inputs = torch.as_tensor(row["input_ids"])
        mask = torch.as_tensor(row["attention_mask"])
        target = torch.as_tensor(row["target_ids"])
        if inputs.shape != (self.sequence_length,) or inputs.dtype not in (torch.int32, torch.int64):
            raise ValueError("IntRR compression requires normalized integer TIGER input_ids.")
        if mask.shape != inputs.shape or not torch.equal(mask, inputs.ne(-1).to(mask.dtype)):
            raise ValueError("IntRR compression requires the normalized TIGER attention mask.")
        if target.shape != (self.catalog.num_hierarchies,):
            raise ValueError("IntRR compression requires one complete target SID.")
        self.catalog.uids_from_semantic_ids(target.unsqueeze(0))

        groups = inputs.reshape(-1, self.catalog.num_hierarchies)
        nonpadding = (~groups.eq(-1).all(dim=1)).nonzero().flatten()
        if not nonpadding.numel():
            raise ValueError("IntRR compression requires history and one target placeholder.")
        placeholder_index = int(nonpadding[-1])
        placeholder = groups.new_full((self.catalog.num_hierarchies,), -1)
        placeholder[0] = 0
        if placeholder_index < 1 or not torch.equal(groups[placeholder_index], placeholder):
            raise ValueError("IntRR compression requires history followed by one TIGER target placeholder.")
        history = groups[:placeholder_index]
        if (history < 0).any():
            raise ValueError("IntRR history contains a partial SID or misplaced padding/placeholder.")
        uids = self.catalog.uids_from_semantic_ids(history)
        compressed = torch.full((self.max_history_items,), -1, dtype=torch.long)
        compressed[: len(uids)] = uids
        result = dict(row)
        result["input_ids"] = compressed
        result["attention_mask"] = compressed.ne(-1).long()
        return result


def intrr_collate(rows, catalog, sequence_length=180, **collate_kwargs):
    """保留原 TIGER 预处理列表，在公共 collate 前完成最后一步压缩。"""
    compress = CompressTigerHistory(catalog, sequence_length)
    return collate_fn_sequence([compress(row) for row in rows], **collate_kwargs)
