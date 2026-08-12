from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetConfig:
    id: str
    filename: str
    records: int
    bytes: int
    sha256: str
    artifact_url: str | None
    text_field: str
    payload_fields: tuple[str, ...]
    relevance_fields: tuple[str, ...]
    benchmark: Path


@dataclass(frozen=True)
class ModelConfig:
    id: str
    huggingface_id: str
    revision: str | None
    dimension: int
    normalize_embeddings: bool
    distance: str
    batch_size: int


@dataclass(frozen=True)
class ExperimentConfig:
    id: str
    dataset: DatasetConfig
    model: ModelConfig
    collection: str
    top_k: int
    posthoc_caps: tuple[int, ...]
    initial_fetch: int
    fetch_step: int


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_dataset(path: Path) -> DatasetConfig:
    raw = read_json(path)
    return DatasetConfig(
        id=raw["id"],
        filename=raw["filename"],
        records=raw["records"],
        bytes=raw["bytes"],
        sha256=raw["sha256"].lower(),
        artifact_url=raw.get("artifact_url"),
        text_field=raw.get("text_field", "text"),
        payload_fields=tuple(raw["payload_fields"]),
        relevance_fields=tuple(raw["relevance_fields"]),
        benchmark=(path.parent / raw["benchmark"]).resolve(),
    )


def load_model(path: Path) -> ModelConfig:
    raw = read_json(path)
    return ModelConfig(
        id=raw["id"],
        huggingface_id=raw["huggingface_id"],
        revision=raw.get("revision"),
        dimension=raw["dimension"],
        normalize_embeddings=raw["normalize_embeddings"],
        distance=raw["distance"],
        batch_size=raw["batch_size"],
    )


def load_experiment(path: Path) -> ExperimentConfig:
    raw = read_json(path)
    dataset = load_dataset((path.parent / raw["dataset_config"]).resolve())
    if raw.get("benchmark"):
        dataset = replace(dataset, benchmark=(path.parent / raw["benchmark"]).resolve())
    model = load_model((path.parent / raw["model_config"]).resolve())
    return ExperimentConfig(
        id=raw["id"],
        dataset=dataset,
        model=model,
        collection=raw["collection"],
        top_k=raw.get("top_k", 5),
        posthoc_caps=tuple(raw.get("posthoc_caps", [25, 100, 200, 400, 2000])),
        initial_fetch=raw.get("initial_fetch", 25),
        fetch_step=raw.get("fetch_step", 25),
    )
