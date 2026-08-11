from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any, Iterable


@dataclass(frozen=True)
class HitMetrics:
    relevant_count: int
    valid_at_k: float
    success_at_k: float
    mean_score: float


def is_relevant(payload: dict[str, Any], target_types: Iterable[str], fields: Iterable[str]) -> bool:
    targets = set(target_types)
    return any(set(payload.get(field, [])) & targets for field in fields)


def evaluate_hits(hits, target_types, relevance_fields, k: int) -> HitMetrics:
    relevant_count = sum(
        is_relevant(hit.payload or {}, target_types, relevance_fields) for hit in hits
    )
    scores = [hit.score for hit in hits if hit.score is not None]
    return HitMetrics(
        relevant_count=relevant_count,
        valid_at_k=relevant_count / k if k else 0.0,
        success_at_k=float(relevant_count == k),
        mean_score=mean(scores) if scores else 0.0,
    )

