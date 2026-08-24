from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .catalog import compact_type_label, find_experiment
from .config import ExperimentConfig
from .index import verify_collection
from .metrics import evaluate_hits, is_relevant


class SearchService:
    def __init__(
        self,
        *,
        root: Path | None = None,
        data_dir: Path | None = None,
        qdrant_url: str = "http://localhost:6333",
        client_factory: Callable[[str], Any] | None = None,
        model_factory: Callable[[ExperimentConfig], Any] | None = None,
        verify_ready: bool = True,
    ) -> None:
        self.root = root
        self.data_dir = data_dir
        self.qdrant_url = qdrant_url
        self.client_factory = client_factory or self._default_client
        self.model_factory = model_factory or self._default_model
        self.verify_ready = verify_ready
        self._models: dict[tuple[str, str | None], Any] = {}

    def run(
        self,
        *,
        dataset_id: str,
        model_id: str,
        query: str,
        constraint_uris: list[str],
        posthoc_cap: int | None = None,
    ) -> dict:
        cleaned_query = query.strip()
        if not cleaned_query:
            raise ValueError("Query cannot be empty.")
        if not constraint_uris:
            raise ValueError("Select at least one ontology constraint.")

        experiment = find_experiment(dataset_id, model_id, root=self.root)
        if self.verify_ready:
            verify_collection(experiment, self.qdrant_url)
        model = self._model(experiment)
        client = self.client_factory(self.qdrant_url)
        vector = self._encode_query(model, experiment, cleaned_query)
        cap = posthoc_cap or max(experiment.posthoc_caps)

        unconstrained, elapsed = self._query(
            client, experiment.collection, vector, experiment.top_k
        )
        prehoc, prehoc_elapsed = self._query(
            client,
            experiment.collection,
            vector,
            experiment.top_k,
            _pre_filter(experiment, constraint_uris),
        )
        posthoc, posthoc_elapsed, examined, requests, transferred = self._posthoc(
            client, experiment, vector, constraint_uris, cap
        )

        return {
            "dataset_id": experiment.dataset.id,
            "model_id": experiment.model.id,
            "collection": experiment.collection,
            "query": cleaned_query,
            "constraints": [
                {"uri": value, "label": compact_type_label(value)} for value in constraint_uris
            ],
            "top_k": experiment.top_k,
            "results": [
                self._group(
                    "unconstrained",
                    experiment,
                    constraint_uris,
                    unconstrained,
                    elapsed,
                    examined=len(unconstrained),
                    requests=1,
                    transferred=len(unconstrained),
                    retrieval_limit=experiment.top_k,
                ),
                self._group(
                    "pre-hoc",
                    experiment,
                    constraint_uris,
                    prehoc,
                    prehoc_elapsed,
                    examined=len(prehoc),
                    requests=1,
                    transferred=len(prehoc),
                    retrieval_limit=experiment.top_k,
                ),
                self._group(
                    "post-hoc",
                    experiment,
                    constraint_uris,
                    posthoc,
                    posthoc_elapsed,
                    examined=examined,
                    requests=requests,
                    transferred=transferred,
                    retrieval_limit=cap,
                ),
            ],
        }

    def _model(self, experiment: ExperimentConfig) -> Any:
        key = (experiment.model.huggingface_id, experiment.model.revision)
        if key not in self._models:
            self._models[key] = self.model_factory(experiment)
        return self._models[key]

    @staticmethod
    def _default_client(qdrant_url: str) -> Any:
        from qdrant_client import QdrantClient

        return QdrantClient(url=qdrant_url)

    @staticmethod
    def _default_model(experiment: ExperimentConfig) -> Any:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(
            experiment.model.huggingface_id,
            revision=experiment.model.revision,
        )

    @staticmethod
    def _encode_query(model: Any, experiment: ExperimentConfig, query: str) -> list[float]:
        vector = model.encode(
            [query],
            normalize_embeddings=experiment.model.normalize_embeddings,
        )[0]
        return vector.tolist() if hasattr(vector, "tolist") else list(vector)

    @staticmethod
    def _query(
        client: Any,
        collection: str,
        vector: list[float],
        limit: int,
        query_filter: Any | None = None,
    ) -> tuple[list[Any], float]:
        start = time.perf_counter()
        hits = client.query_points(
            collection_name=collection,
            query=vector,
            limit=limit,
            with_payload=True,
            query_filter=query_filter,
        ).points
        return hits, time.perf_counter() - start

    def _posthoc(
        self,
        client: Any,
        experiment: ExperimentConfig,
        vector: list[float],
        constraint_uris: list[str],
        cap: int,
    ) -> tuple[list[Any], float, int, int, int]:
        accepted = []
        accepted_ids = set()
        current_limit = experiment.initial_fetch
        examined = 0
        requests = 0
        transferred = 0
        elapsed = 0.0
        while current_limit <= cap and len(accepted) < experiment.top_k:
            hits, request_time = self._query(client, experiment.collection, vector, current_limit)
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
                    hit.payload or {},
                    constraint_uris,
                    experiment.dataset.relevance_fields,
                ):
                    accepted.append(hit)
                    accepted_ids.add(identity)
                    if len(accepted) == experiment.top_k:
                        break
            if len(hits) < current_limit:
                break
            current_limit += experiment.fetch_step
        return accepted, elapsed, examined, requests, transferred

    @staticmethod
    def _group(
        strategy: str,
        experiment: ExperimentConfig,
        constraint_uris: list[str],
        hits: list[Any],
        elapsed: float,
        *,
        examined: int,
        requests: int,
        transferred: int,
        retrieval_limit: int,
    ) -> dict:
        metrics = evaluate_hits(
            hits,
            constraint_uris,
            experiment.dataset.relevance_fields,
            experiment.top_k,
        )
        return {
            "strategy": strategy,
            "retrieval_limit": retrieval_limit,
            "valid_at_k": metrics.valid_at_k,
            "success_at_k": metrics.success_at_k,
            "mean_score": metrics.mean_score,
            "time_seconds": elapsed,
            "examined": examined,
            "requests": requests,
            "candidates_transferred": transferred,
            "hits": [
                _hit_row(rank, hit, constraint_uris, experiment.dataset.relevance_fields)
                for rank, hit in enumerate(hits, start=1)
            ],
        }


def _pre_filter(experiment: ExperimentConfig, constraint_uris: list[str]) -> Any:
    try:
        from qdrant_client import models
    except ImportError:
        return {
            "must": [
                {
                    "key": experiment.dataset.relevance_fields[0],
                    "match": {"any": constraint_uris},
                }
            ]
        }
    return models.Filter(
        must=[
            models.FieldCondition(
                key=experiment.dataset.relevance_fields[0],
                match=models.MatchAny(any=constraint_uris),
            )
        ]
    )


def _hit_row(
    rank: int,
    hit: Any,
    constraint_uris: list[str],
    relevance_fields: tuple[str, ...],
) -> dict:
    payload = hit.payload or {}
    matched = _matched_types(payload, constraint_uris, relevance_fields)
    return {
        "rank": rank,
        "point_id": str(hit.id),
        "score": hit.score,
        "valid": bool(matched),
        "matched_types": [{"uri": value, "label": compact_type_label(value)} for value in matched],
        "payload": payload,
    }


def _matched_types(
    payload: dict[str, Any],
    constraint_uris: list[str],
    relevance_fields: tuple[str, ...],
) -> list[str]:
    targets = set(constraint_uris)
    matches = set()
    for field in relevance_fields:
        values = payload.get(field, [])
        if isinstance(values, list):
            matches.update(str(value) for value in values if str(value) in targets)
    return sorted(matches, key=lambda value: compact_type_label(value).lower())
