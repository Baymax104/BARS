"""冻结 keyed 预测的用户配对贡献分析；不装配或前向推荐模型。"""

import copy
import hashlib
import math
import re
from collections.abc import Mapping

import numpy as np
import torch
from lightning import LightningModule
from omegaconf import OmegaConf

from src.common.writers.structured_analysis import StructuredAnalysisOutput
from src.data.components.data_models import ModelOutput
from src.data.utils import gather_predictions_by_keys

METRIC_NAMES = ("recall@5", "ndcg@5", "recall@10", "ndcg@10")
INTEGER_DTYPES = (torch.uint8, torch.int8, torch.int16, torch.int32, torch.int64)


def _integer_tensor(value, description):
    tensor = torch.as_tensor(value).detach().cpu()
    if tensor.dtype not in INTEGER_DTYPES:
        raise ValueError(f"{description} must contain integers.")
    return tensor.long()


def _metrics(predictions, labels):
    hits = (predictions == labels[:, None]).all(-1)
    ranks = torch.where(hits.any(-1), hits.long().argmax(-1) + 1, 0).numpy()
    values = []
    for k in (5, 10):
        hit = (ranks > 0) & (ranks <= k)
        values.extend((hit.astype(np.float64), hit / np.log2(np.maximum(ranks, 1) + 1)))
    return ranks, np.column_stack(values)


class CoPMRecContributionDiagnosis(LightningModule):
    """用真实测试标签测量冻结列表，所有比较方向为 reference 减 comparison。"""

    def __init__(
        self,
        *,
        prediction_bundles,
        semantic_ids,
        input_references=None,
        bootstrap_repetitions=2000,
        reference="untied",
        num_hierarchies=4,
    ):
        super().__init__()
        if type(num_hierarchies) is not int or num_hierarchies < 1:
            raise ValueError("SID depth must be a positive integer.")
        if type(bootstrap_repetitions) is not int or bootstrap_repetitions < 1:
            raise ValueError("Bootstrap repetitions must be a positive integer.")
        if (
            not isinstance(prediction_bundles, Mapping)
            or len(prediction_bundles) < 2
            or reference not in prediction_bundles
        ):
            raise ValueError("Contribution analysis requires at least two conditions including its reference.")
        references = (
            OmegaConf.to_container(input_references, resolve=True)
            if OmegaConf.is_config(input_references)
            else copy.deepcopy(input_references)
        )
        if isinstance(references, Mapping) and (
            references.get("dataset", "beauty") != "beauty" or references.get("training_seed", 42) != 42
        ):
            raise ValueError("This mechanism stage is fixed to Beauty/seed42.")
        catalog = _integer_tensor(semantic_ids, "Catalog SIDs")
        if catalog.ndim != 2 or catalog.shape[1] != num_hierarchies or len(catalog) < 10 or (catalog < 0).any():
            raise ValueError("Catalog must contain at least ten complete nonnegative SIDs.")
        self.catalog_rows = {tuple(sid): index for index, sid in enumerate(catalog.tolist())}
        if len(self.catalog_rows) != len(catalog):
            raise ValueError("Catalog SIDs must be unique.")
        self.num_hierarchies = num_hierarchies
        self.reference = reference
        self.bootstrap_repetitions = bootstrap_repetitions
        self.prediction_bundles = {}
        for name, bundle in prediction_bundles.items():
            if not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9_]+", name) is None:
                raise ValueError("Condition names must be nonempty letters, digits or underscores.")
            if not isinstance(bundle, ModelOutput):
                raise TypeError("Prediction sources must be keyed ModelOutput bundles.")
            keys = _integer_tensor(bundle.keys, "Prediction user keys")
            predictions = _integer_tensor(bundle.predictions, "Predictions")
            if keys.ndim != 1 or not len(keys) or len(keys.unique()) != len(keys):
                raise ValueError("Prediction user keys must be a nonempty unique vector.")
            if predictions.shape != (len(keys), 10, num_hierarchies):
                raise ValueError("Contribution analysis requires complete Top10 SIDs.")
            for row in predictions.tolist():
                sids = [tuple(sid) for sid in row]
                if len(set(sids)) != 10 or any(sid not in self.catalog_rows for sid in sids):
                    raise ValueError("Prediction Top10 must contain legal unique catalog SIDs.")
            order = keys.argsort()
            self.prediction_bundles[name] = ModelOutput(
                keys[order], predictions[order], copy.deepcopy(bundle.auxiliary)
            )
        reference_keys = self.prediction_bundles[reference].keys
        if any(not torch.equal(bundle.keys, reference_keys) for bundle in self.prediction_bundles.values()):
            raise ValueError("Prediction sources must contain exactly the same user population.")
        self.metadata = dict(
            protocol="bars-untied-mechanism-beauty42-20261019-v1",
            analysis_protocol="bars-untied-contributions-20261019-v1",
            evidence_type="frozen_predictions_paired_contributions",
            reference=reference,
            difference_direction="reference_minus_comparison",
            relative_change_denominator="comparison",
            model_forward_count=0,
            optimizer_updates=0,
            bootstrap=dict(
                rng="PCG64",
                seed=42,
                repetitions=bootstrap_repetitions,
                confidence=0.95,
                interval="pointwise_percentile",
                shared_samples_across_metrics=True,
            ),
            uncertainty_scope="users_at_fixed_training_sources_not_training_seeds",
            input_references=references,
            prediction_source_metadata={
                name: copy.deepcopy(bundle.auxiliary) for name, bundle in self.prediction_bundles.items()
            },
        )
        self._keys, self._labels, self._observed_keys = [], [], set()

    def on_test_start(self):
        if self.trainer.world_size != 1:
            raise ValueError("Contribution analysis requires one process.")
        self._keys.clear()
        self._labels.clear()
        self._observed_keys.clear()

    @torch.no_grad()
    def test_step(self, batch, batch_idx):
        inputs, label = batch
        if label is None or inputs.output_keys is None:
            raise ValueError("Contribution analysis requires real labels and business user keys.")
        keys = _integer_tensor(inputs.output_keys, "Testing user keys")
        labels = _integer_tensor(label.target_ids, "Testing target SIDs")
        if keys.ndim != 1 or not len(keys) or labels.shape != (len(keys), self.num_hierarchies):
            raise ValueError("Testing user keys and target SIDs must have aligned rows.")
        if len(keys.unique()) != len(keys) or self._observed_keys.intersection(keys.tolist()):
            raise ValueError("Testing contains duplicate user keys.")
        if any(tuple(sid) not in self.catalog_rows for sid in labels.tolist()):
            raise ValueError("Testing target SID is absent from the catalog.")
        # 仅以 key 查询冻结预测；真实目标只进入度量与分解。
        gather_predictions_by_keys(self.prediction_bundles[self.reference], keys)
        self._observed_keys.update(keys.tolist())
        self._keys.append(keys)
        self._labels.append(labels)
        return {}

    def structured_analysis_output(self):
        if not self._keys:
            raise ValueError("Contribution analysis has no testing observations.")
        keys = torch.cat(self._keys)
        labels = torch.cat(self._labels)
        order = keys.argsort()
        keys, labels = keys[order], labels[order]
        if not torch.equal(keys, self.prediction_bundles[self.reference].keys):
            raise ValueError("Prediction and testing user populations differ.")
        names = sorted(self.prediction_bundles)
        predictions = {name: gather_predictions_by_keys(self.prediction_bundles[name], keys) for name in names}
        measured = {name: _metrics(predictions[name], labels) for name in names}
        reference_values = measured[self.reference][1]
        comparisons = [name for name in names if name != self.reference]
        delta = np.concatenate([reference_values - measured[name][1] for name in comparisons], axis=1)
        rng = np.random.Generator(np.random.PCG64(42))
        bootstrap = np.stack(
            [delta[rng.integers(len(keys), size=len(keys))].mean(0) for _ in range(self.bootstrap_repetitions)]
        )
        intervals = np.quantile(bootstrap, [0.025, 0.975], axis=0)
        users, pairs, cases, observations = [], [], [], []
        for name in names:
            ranks, values = measured[name]
            observations.append(
                dict(condition=name, n=len(keys), **dict(zip(METRIC_NAMES, values.mean(0).tolist(), strict=True)))
            )
            for i, (key, label_sid) in enumerate(zip(keys.tolist(), labels.tolist(), strict=True)):
                row = dict(
                    user_key=key,
                    target_sid=label_sid,
                    target_row=self.catalog_rows[tuple(label_sid)],
                    condition=name,
                    reference=self.reference,
                    target_rank=int(ranks[i]) if ranks[i] else None,
                    **dict(zip(METRIC_NAMES, values[i].tolist(), strict=True)),
                )
                for k in (5, 10):
                    j = METRIC_NAMES.index(f"ndcg@{k}")
                    reference_hit, comparison_hit = reference_values[i, j] > 0, values[i, j] > 0
                    category = (
                        "common_rank"
                        if reference_hit and comparison_hit
                        else "gain"
                        if reference_hit
                        else "loss"
                        if comparison_hit
                        else "neither"
                    )
                    difference = float(reference_values[i, j] - values[i, j])
                    row[f"hit_class@{k}"] = category
                    row[f"signed_ndcg_difference@{k}"] = difference
                    for component in ("gain", "loss", "common_rank"):
                        row[f"contribution_{component}@{k}"] = difference if category == component else 0.0
                users.append(row)
        for comparison_index, name in enumerate(comparisons):
            other_values = measured[name][1]
            for metric_index, metric in enumerate(METRIC_NAMES):
                j = comparison_index * len(METRIC_NAMES) + metric_index
                current_delta = delta[:, j]
                reference_hit, comparison_hit = reference_values[:, metric_index] > 0, other_values[:, metric_index] > 0
                categories = dict(
                    gain=reference_hit & ~comparison_hit,
                    loss=~reference_hit & comparison_hit,
                    common_rank=reference_hit & comparison_hit,
                )
                contributions = {
                    f"contribution_{category}": float(np.where(selected, current_delta, 0).mean())
                    for category, selected in categories.items()
                }
                signed_difference = float(current_delta.mean())
                if not math.isclose(sum(contributions.values()), signed_difference, rel_tol=1e-12, abs_tol=1e-15):
                    raise ValueError("Paired contributions do not sum to the observed metric difference.")
                comparison_mean = float(other_values[:, metric_index].mean())
                pairs.append(
                    dict(
                        reference=self.reference,
                        comparison=name,
                        metric=metric,
                        n=len(keys),
                        reference_mean=float(reference_values[:, metric_index].mean()),
                        comparison_mean=comparison_mean,
                        signed_difference=signed_difference,
                        relative_percent=100 * signed_difference / comparison_mean if comparison_mean else None,
                        ci_low=float(intervals[0, j]),
                        ci_high=float(intervals[1, j]),
                        **contributions,
                    )
                )
            for k in (5, 10):
                metric_index = METRIC_NAMES.index(f"ndcg@{k}")
                reference_hit, comparison_hit = reference_values[:, metric_index] > 0, other_values[:, metric_index] > 0
                categories = dict(
                    gain=reference_hit & ~comparison_hit,
                    loss=~reference_hit & comparison_hit,
                    common=reference_hit & comparison_hit,
                    neither=~reference_hit & ~comparison_hit,
                )
                for category, selected in categories.items():
                    pairs.append(
                        dict(
                            reference=self.reference,
                            comparison=name,
                            metric=f"hit_class@{k}",
                            category=category,
                            n=len(keys),
                            count=int(selected.sum()),
                            fraction=float(selected.mean()),
                        )
                    )
                    selected_indices = sorted(
                        np.flatnonzero(selected).tolist(),
                        key=lambda i: hashlib.sha256(str(int(keys[i])).encode()).hexdigest(),
                    )
                    for i in selected_indices[:3]:
                        cases.append(
                            dict(
                                reference=self.reference,
                                comparison=name,
                                case_k=k,
                                category=category,
                                user_key=int(keys[i]),
                                target_sid=labels[i].tolist(),
                                reference_rank=int(measured[self.reference][0][i]) or None,
                                comparison_rank=int(measured[name][0][i]) or None,
                                signed_ndcg_difference=float(
                                    reference_values[i, metric_index] - other_values[i, metric_index]
                                ),
                                selection="first_three_sha256_user_key",
                            )
                        )
        key_labels = torch.cat((keys[:, None], labels), dim=1).numpy().astype("<i8", copy=False)
        metadata = {
            **self.metadata,
            "user_count": len(keys),
            "user_label_sha256": hashlib.sha256(key_labels.tobytes()).hexdigest(),
            "user_label_hash_recipe": "sorted key then full SID; little-endian int64 row-major",
        }
        return StructuredAnalysisOutput(
            documents={"summary.json": dict(metadata=metadata, observations=observations, comparisons=pairs)},
            tables={"users.csv": users, "comparisons.csv": pairs, "cases.csv": cases},
            bundles={f"{name}.pt": dict(keys=keys, predictions=predictions[name]) for name in names},
            metadata=metadata,
        )
