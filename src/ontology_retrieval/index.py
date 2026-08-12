from __future__ import annotations

import uuid
from pathlib import Path

from .config import ExperimentConfig
from .datasets import iter_entity_cards, verify_dataset


def stable_point_id(dataset_id: str, iri: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{dataset_id}:{iri}"))


def build_collection(
    experiment: ExperimentConfig,
    dataset_path: Path,
    qdrant_url: str,
    replace: bool = False,
    resume: bool = False,
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
        )
        for field in experiment.dataset.relevance_fields:
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
    return len(existing_ids) + total


def verify_collection_shape(experiment: ExperimentConfig, client) -> None:
    info = client.get_collection(experiment.collection)
    vector_config = info.config.params.vectors
    errors = []
    if vector_config.size != experiment.model.dimension:
        errors.append(f"dimension expected {experiment.model.dimension}, found {vector_config.size}")
    if str(vector_config.distance).lower().split(".")[-1] != experiment.model.distance.lower():
        errors.append(f"distance expected {experiment.model.distance}, found {vector_config.distance}")
    if info.points_count > experiment.dataset.records:
        errors.append(f"points exceed expected {experiment.dataset.records}: {info.points_count}")
    if errors:
        raise ValueError("Cannot resume incompatible collection: " + "; ".join(errors))


def verify_collection(experiment: ExperimentConfig, qdrant_url: str) -> dict:
    from qdrant_client import QdrantClient

    client = QdrantClient(url=qdrant_url)
    info = client.get_collection(experiment.collection)
    vector_config = info.config.params.vectors
    errors = []
    if info.points_count != experiment.dataset.records:
        errors.append(f"points expected {experiment.dataset.records}, found {info.points_count}")
    if vector_config.size != experiment.model.dimension:
        errors.append(f"dimension expected {experiment.model.dimension}, found {vector_config.size}")
    if errors:
        raise ValueError("Collection verification failed: " + "; ".join(errors))
    return {
        "collection": experiment.collection,
        "status": str(info.status),
        "points": info.points_count,
        "dimension": vector_config.size,
        "distance": str(vector_config.distance),
    }
