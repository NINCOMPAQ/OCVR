from __future__ import annotations

import time
import uuid
from math import ceil
from pathlib import Path

from .config import ExperimentConfig
from .datasets import iter_entity_cards, verify_dataset

HNSW_M = 16
HNSW_EF_CONSTRUCT = 100
HNSW_ON_DISK = False
FULL_SCAN_THRESHOLD_KB = 1000
INDEXING_THRESHOLD_KB = 1000
DEFAULT_SEGMENT_NUMBER = 1
READINESS_POLL_SECONDS = 2.0
REQUIRED_PAYLOAD_INDEXES = ("types", "types_closure")


def stable_point_id(dataset_id: str, iri: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{dataset_id}:{iri}"))


def build_collection(
    experiment: ExperimentConfig,
    dataset_path: Path,
    qdrant_url: str,
    replace: bool = False,
    resume: bool = False,
    ready_timeout_seconds: float = 1800.0,
) -> int:
    from qdrant_client import QdrantClient, models
    from sentence_transformers import SentenceTransformer

    verify_dataset(dataset_path, experiment.dataset)
    client = QdrantClient(url=qdrant_url)
    exists = client.collection_exists(experiment.collection)
    if replace and resume:
        raise ValueError("--replace and --resume cannot be used together")
    if exists and not replace and not resume:
        raise RuntimeError(
            f"Collection {experiment.collection!r} already exists; pass --replace or --resume."
        )
    if exists and replace:
        client.delete_collection(experiment.collection)
    distance = getattr(models.Distance, experiment.model.distance.upper())
    existing_ids = set()
    if exists and resume:
        verify_collection_shape(experiment, client)
        offset = None
        while True:
            points, offset = client.scroll(
                collection_name=experiment.collection,
                limit=1000,
                offset=offset,
                with_payload=False,
                with_vectors=False,
            )
            existing_ids.update(str(point.id) for point in points)
            if offset is None:
                break
    else:
        client.create_collection(
            collection_name=experiment.collection,
            vectors_config=models.VectorParams(size=experiment.model.dimension, distance=distance),
            hnsw_config=models.HnswConfigDiff(
                m=HNSW_M,
                ef_construct=HNSW_EF_CONSTRUCT,
                full_scan_threshold=FULL_SCAN_THRESHOLD_KB,
                on_disk=HNSW_ON_DISK,
            ),
            optimizers_config=models.OptimizersConfigDiff(
                default_segment_number=DEFAULT_SEGMENT_NUMBER,
                indexing_threshold=INDEXING_THRESHOLD_KB,
            ),
        )
        for field in REQUIRED_PAYLOAD_INDEXES:
            client.create_payload_index(
                collection_name=experiment.collection,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
                wait=True,
            )
    model = SentenceTransformer(
        experiment.model.huggingface_id,
        revision=experiment.model.revision,
    )
    dimension = model.get_embedding_dimension()
    if dimension != experiment.model.dimension:
        raise ValueError(
            f"Model dimension {dimension} does not match configured {experiment.model.dimension}"
        )
    total = 0
    batch: list[dict] = []

    def flush() -> None:
        nonlocal total
        if not batch:
            return
        texts = [record[experiment.dataset.text_field] for record in batch]
        vectors = model.encode(
            texts,
            batch_size=experiment.model.batch_size,
            normalize_embeddings=experiment.model.normalize_embeddings,
            show_progress_bar=False,
        )
        points = []
        for record, vector in zip(batch, vectors, strict=True):
            payload = {key: record.get(key) for key in experiment.dataset.payload_fields}
            payload["iri"] = record["iri"]
            points.append(
                models.PointStruct(
                    id=stable_point_id(experiment.dataset.id, record["iri"]),
                    vector=vector.tolist(),
                    payload=payload,
                )
            )
        client.upsert(experiment.collection, points=points, wait=True)
        total += len(points)
        batch.clear()

    for record in iter_entity_cards(dataset_path):
        if stable_point_id(experiment.dataset.id, record["iri"]) in existing_ids:
            continue
        batch.append(record)
        if len(batch) >= experiment.model.batch_size:
            flush()
    flush()
    wait_for_collection_ready(
        experiment,
        client=client,
        timeout_seconds=ready_timeout_seconds,
    )
    return len(existing_ids) + total


def verify_collection_shape(experiment: ExperimentConfig, client) -> None:
    info = client.get_collection(experiment.collection)
    errors = _configuration_errors(experiment, info)
    if _enum_value(info.status) == "red":
        errors.append("collection status is red")
    if info.points_count > experiment.dataset.records:
        errors.append(f"points exceed expected {experiment.dataset.records}: {info.points_count}")
    if errors:
        raise ValueError("Cannot resume incompatible collection: " + "; ".join(errors))


def verify_collection(experiment: ExperimentConfig, qdrant_url: str) -> dict:
    from qdrant_client import QdrantClient

    client = QdrantClient(url=qdrant_url)
    info = client.get_collection(experiment.collection)
    errors = _configuration_errors(experiment, info)
    if _enum_value(info.status) != "green":
        errors.append(f"status expected green, found {_enum_value(info.status)}")
    if info.points_count != experiment.dataset.records:
        errors.append(f"points expected {experiment.dataset.records}, found {info.points_count}")
    maximum_unindexed = _maximum_unindexed_vectors(experiment)
    minimum_indexed = experiment.dataset.records - maximum_unindexed
    if info.indexed_vectors_count < minimum_indexed:
        errors.append(
            "indexed vectors below readiness threshold: "
            f"expected at least {minimum_indexed} "
            f"(at most {maximum_unindexed} below the optimizer threshold), "
            f"found {info.indexed_vectors_count}"
        )
    if errors:
        raise ValueError(
            f"Collection {experiment.collection!r} is not benchmark-ready: " + "; ".join(errors)
        )
    return _collection_report(experiment, info)


def wait_for_collection_ready(
    experiment: ExperimentConfig,
    qdrant_url: str | None = None,
    *,
    client=None,
    timeout_seconds: float = 1800.0,
) -> dict:
    if client is None:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=qdrant_url)
    deadline = time.monotonic() + timeout_seconds
    last_error = "collection state was not checked"
    while True:
        try:
            info = client.get_collection(experiment.collection)
            configuration_errors = _configuration_errors(experiment, info)
            if configuration_errors:
                raise ValueError(
                    f"Collection {experiment.collection!r} has incompatible configuration: "
                    + "; ".join(configuration_errors)
                )
            errors = []
            if _enum_value(info.status) != "green":
                errors.append(f"status expected green, found {_enum_value(info.status)}")
            if info.points_count != experiment.dataset.records:
                errors.append(
                    f"points expected {experiment.dataset.records}, found {info.points_count}"
                )
            maximum_unindexed = _maximum_unindexed_vectors(experiment)
            minimum_indexed = experiment.dataset.records - maximum_unindexed
            if info.indexed_vectors_count < minimum_indexed:
                errors.append(
                    f"indexed vectors expected at least {minimum_indexed}, "
                    f"found {info.indexed_vectors_count}"
                )
            if not errors:
                return _collection_report(experiment, info)
            last_error = "; ".join(errors)
        except ValueError:
            raise
        # Qdrant client failures can surface as several transport-specific exception
        # classes. Treat them as transient while waiting, and report the final error
        # if the readiness deadline expires.
        except Exception as error:  # noqa: BLE001
            last_error = str(error)
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Timed out after {timeout_seconds:g}s waiting for collection "
                f"{experiment.collection!r} to become benchmark-ready. Last state: {last_error}"
            )
        time.sleep(READINESS_POLL_SECONDS)


def _configuration_errors(experiment: ExperimentConfig, info) -> list[str]:
    vector_config = info.config.params.vectors
    errors = []
    if vector_config.size != experiment.model.dimension:
        errors.append(
            f"dimension expected {experiment.model.dimension}, found {vector_config.size}"
        )
    if _enum_value(vector_config.distance) != experiment.model.distance.lower():
        errors.append(
            f"distance expected {experiment.model.distance}, found {vector_config.distance}"
        )
    hnsw = info.config.hnsw_config
    expected_hnsw = {
        "m": HNSW_M,
        "ef_construct": HNSW_EF_CONSTRUCT,
        "full_scan_threshold": FULL_SCAN_THRESHOLD_KB,
        "on_disk": HNSW_ON_DISK,
    }
    for field, expected in expected_hnsw.items():
        actual = getattr(hnsw, field)
        if actual != expected:
            errors.append(f"HNSW {field} expected {expected}, found {actual}")
    optimizer = info.config.optimizer_config
    expected_optimizer = {
        "default_segment_number": DEFAULT_SEGMENT_NUMBER,
        "indexing_threshold": INDEXING_THRESHOLD_KB,
    }
    for field, expected in expected_optimizer.items():
        actual = getattr(optimizer, field)
        if actual != expected:
            errors.append(f"optimizer {field} expected {expected}, found {actual}")
    for field in REQUIRED_PAYLOAD_INDEXES:
        schema = info.payload_schema.get(field)
        if schema is None:
            errors.append(f"missing payload index {field!r}")
        elif _enum_value(schema.data_type) != "keyword":
            errors.append(f"payload index {field!r} expected keyword, found {schema.data_type}")
    return errors


def _enum_value(value) -> str:
    raw = getattr(value, "value", value)
    return str(raw).lower().split(".")[-1]


def _maximum_unindexed_vectors(experiment: ExperimentConfig) -> int:
    # Qdrant defines 1 KB of indexing threshold as one 256-dimensional vector.
    return ceil(INDEXING_THRESHOLD_KB * 256 / experiment.model.dimension)


def _collection_report(experiment: ExperimentConfig, info) -> dict:
    vector_config = info.config.params.vectors
    return {
        "collection": experiment.collection,
        "status": _enum_value(info.status),
        "points": info.points_count,
        "indexed_vectors": info.indexed_vectors_count,
        "indexed_fraction": info.indexed_vectors_count / experiment.dataset.records,
        "maximum_unindexed_vectors": _maximum_unindexed_vectors(experiment),
        "segments": info.segments_count,
        "dimension": vector_config.size,
        "distance": _enum_value(vector_config.distance),
        "hnsw": {
            "m": info.config.hnsw_config.m,
            "ef_construct": info.config.hnsw_config.ef_construct,
            "full_scan_threshold_kb": info.config.hnsw_config.full_scan_threshold,
            "on_disk": info.config.hnsw_config.on_disk,
        },
        "optimizer": {
            "default_segment_number": info.config.optimizer_config.default_segment_number,
            "indexing_threshold_kb": info.config.optimizer_config.indexing_threshold,
        },
        "payload_indexes": {
            field: _enum_value(info.payload_schema[field].data_type)
            for field in REQUIRED_PAYLOAD_INDEXES
        },
    }
