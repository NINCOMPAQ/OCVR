from __future__ import annotations

import json
import time
from pathlib import Path
from statistics import mean

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from .config import ExperimentConfig
from .metrics import evaluate_hits, is_relevant
from .index import verify_collection


def load_benchmark(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Benchmark must be a non-empty JSON list: {path}")
    return value


def _query(client, collection, vector, limit, query_filter=None):
    start = time.perf_counter()
    hits = client.query_points(
        collection_name=collection,
        query=vector,
        limit=limit,
        with_payload=True,
        query_filter=query_filter,
    ).points
    return hits, time.perf_counter() - start


def _posthoc(client, experiment, vector, target_types, cap):
    accepted = []
    accepted_ids = set()
    current_limit = experiment.initial_fetch
    examined = 0
    requests = 0
    transferred = 0
    elapsed = 0.0
    while current_limit <= cap and len(accepted) < experiment.top_k:
        hits, request_time = _query(client, experiment.collection, vector, current_limit)
        elapsed += request_time
        requests += 1
        transferred += len(hits)
        new_hits = hits[examined:]
        examined = len(hits)
        for hit in new_hits:
            identity = (hit.payload or {}).get("iri", str(hit.id))
            if identity in accepted_ids:
                continue
            if is_relevant(
                hit.payload or {}, target_types, experiment.dataset.relevance_fields
            ):
                accepted.append(hit)
                accepted_ids.add(identity)
                if len(accepted) == experiment.top_k:
                    break
        if len(hits) < current_limit:
            break
        current_limit += experiment.fetch_step
    return accepted, elapsed, examined, requests, transferred


def run_experiment(experiment: ExperimentConfig, qdrant_url: str) -> dict:
    verify_collection(experiment, qdrant_url)
    tests = load_benchmark(experiment.dataset.benchmark)
    model = SentenceTransformer(
        experiment.model.huggingface_id,
        revision=experiment.model.revision,
    )
    client = QdrantClient(url=qdrant_url)
    rows = []
    for test in tests:
        vector = model.encode(
            [test["query"]], normalize_embeddings=experiment.model.normalize_embeddings
        )[0].tolist()
        target_types = test["constraint_any"]
        unconstrained, elapsed = _query(
            client, experiment.collection, vector, experiment.top_k
        )
        metrics = evaluate_hits(
            unconstrained, target_types, experiment.dataset.relevance_fields, experiment.top_k
        )
        rows.append(
            _result(
                test,
                "unconstrained",
                experiment.top_k,
                metrics,
                elapsed,
                5,
                1,
                5,
                unconstrained,
                experiment.dataset.relevance_fields,
            )
        )

        pre_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key=experiment.dataset.relevance_fields[0],
                    match=models.MatchAny(any=target_types),
                )
            ]
        )
        prehoc, elapsed = _query(
            client, experiment.collection, vector, experiment.top_k, pre_filter
        )
        metrics = evaluate_hits(
            prehoc, target_types, experiment.dataset.relevance_fields, experiment.top_k
        )
        rows.append(
            _result(
                test,
                "pre-hoc",
                experiment.top_k,
                metrics,
                elapsed,
                len(prehoc),
                1,
                len(prehoc),
                prehoc,
                experiment.dataset.relevance_fields,
            )
        )

        for cap in experiment.posthoc_caps:
            hits, elapsed, examined, requests, transferred = _posthoc(
                client, experiment, vector, target_types, cap
            )
            metrics = evaluate_hits(
                hits, target_types, experiment.dataset.relevance_fields, experiment.top_k
            )
            rows.append(
                _result(
                    test,
                    "post-hoc",
                    cap,
                    metrics,
                    elapsed,
                    examined,
                    requests,
                    transferred,
                    hits,
                    experiment.dataset.relevance_fields,
                )
            )
    return {
        "schema_version": 2,
        "experiment": experiment.id,
        "dataset": experiment.dataset.id,
        "model": experiment.model.id,
        "collection": experiment.collection,
        "queries": len(tests),
        "results": rows,
        "summary": summarize(rows),
    }


def _result(
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
                "valid": is_relevant(
                    hit.payload or {}, test["constraint_any"], relevance_fields
                ),
                "payload": hit.payload or {},
            }
            for rank, hit in enumerate(hits, start=1)
        ],
    }


def summarize(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, int], list[dict]] = {}
    for row in rows:
        groups.setdefault((row["strategy"], row["retrieval_limit"]), []).append(row)
    output = []
    for (strategy, limit), values in groups.items():
        output.append(
            {
                "strategy": strategy,
                "retrieval_limit": limit,
                "valid_at_5": mean(v["valid_at_5"] for v in values),
                "success_at_5": mean(v["success_at_5"] for v in values),
                "mean_score": mean(v["mean_score"] for v in values),
                "time_seconds": mean(v["time_seconds"] for v in values),
                "examined": mean(v["examined"] for v in values),
                "requests": mean(v["requests"] for v in values),
                "candidates_transferred": mean(v["candidates_transferred"] for v in values),
            }
        )
    return output
