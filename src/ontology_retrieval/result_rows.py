from __future__ import annotations

from .metrics import is_relevant


def build_result(
    test,
    strategy,
    limit,
    metrics,
    elapsed,
    examined,
    requests,
    transferred,
    hits,
    relevance_fields,
):
    return {
        "query_id": test["id"],
        "query": test["query"],
        "constraint_any": test["constraint_any"],
        "strategy": strategy,
        "retrieval_limit": limit,
        "valid_at_5": metrics.valid_at_k,
        "success_at_5": metrics.success_at_k,
        "mean_score": metrics.mean_score,
        "time_seconds": elapsed,
        "examined": examined,
        "requests": requests,
        "candidates_transferred": transferred,
        "hits": [
            {
                "rank": rank,
                "point_id": str(hit.id),
                "score": hit.score,
                "valid": is_relevant(hit.payload or {}, test["constraint_any"], relevance_fields),
                "payload": hit.payload or {},
            }
            for rank, hit in enumerate(hits, start=1)
        ],
    }
