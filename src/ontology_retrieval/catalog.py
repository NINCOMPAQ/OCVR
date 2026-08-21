from __future__ import annotations

import ast
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from urllib.error import URLError
from urllib.parse import unquote
from urllib.request import urlopen

from .config import DatasetConfig, ExperimentConfig, load_experiment
from .datasets import iter_entity_cards

DEFAULT_DATASET_ID = "atmonto-enriched-v1"
DEFAULT_MODEL_ID = "all-MiniLM-L6-v2"


DATASET_LABELS = {
    "atmonto-enriched-v1": "ATMONTO",
    "brick-mortardata-enriched-v1": "Brick/Mortar",
    "dbpedia-us-civic-places-enriched-v1": "DBpedia US civic places",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def dataset_label(dataset: DatasetConfig) -> str:
    return DATASET_LABELS.get(dataset.id, dataset.id)


def compact_type_label(value: str) -> str:
    trimmed = value.rstrip("/")
    if "#" in trimmed:
        label = trimmed.rsplit("#", 1)[1]
    else:
        label = trimmed.rsplit("/", 1)[-1]
    if ":" in label:
        label = label.rsplit(":", 1)[1]
    return unquote(label) or value


def load_app_experiments(root: Path | None = None) -> list[ExperimentConfig]:
    base = root or project_root()
    experiments: list[ExperimentConfig] = []
    seen: set[tuple[str, str]] = set()
    for path in sorted((base / "configs" / "experiments").glob("*.json")):
        experiment = load_experiment(path.resolve())
        key = (experiment.dataset.id, experiment.model.id)
        if key in seen:
            continue
        seen.add(key)
        experiments.append(experiment)
    return experiments


def build_catalog(
    *,
    root: Path | None = None,
    qdrant_url: str | None = None,
    include_readiness: bool = True,
) -> dict:
    experiments = load_app_experiments(root)
    datasets: dict[str, dict] = {}
    models: dict[str, dict] = {}
    experiment_rows = []
    qdrant_reachable = (
        _qdrant_reachable(qdrant_url) if include_readiness and qdrant_url else None
    )

    for experiment in experiments:
        dataset = experiment.dataset
        model = experiment.model
        datasets.setdefault(
            dataset.id,
            {
                "id": dataset.id,
                "label": dataset_label(dataset),
                "records": dataset.records,
                "models": [],
            },
        )["models"].append(model.id)
        models.setdefault(
            model.id,
            {
                "id": model.id,
                "label": model.id,
                "dimension": model.dimension,
                "default": model.id == DEFAULT_MODEL_ID,
            },
        )

        readiness = {"ready": None, "error": None}
        if include_readiness and qdrant_url:
            if qdrant_reachable:
                readiness = collection_readiness(experiment, qdrant_url)
            else:
                readiness = {
                    "ready": False,
                    "error": f"Qdrant is not reachable at {qdrant_url}.",
                }
        experiment_rows.append(
            {
                "dataset_id": dataset.id,
                "model_id": model.id,
                "collection": experiment.collection,
                **readiness,
            }
        )

    return {
        "datasets": sorted(datasets.values(), key=lambda item: item["label"]),
        "models": sorted(
            models.values(), key=lambda item: (not item["default"], item["label"])
        ),
        "experiments": sorted(
            experiment_rows,
            key=lambda item: (item["dataset_id"], item["model_id"]),
        ),
        "defaults": {
            "dataset_id": DEFAULT_DATASET_ID,
            "model_id": DEFAULT_MODEL_ID,
        },
    }


def _qdrant_reachable(qdrant_url: str) -> bool:
    try:
        with urlopen(f"{qdrant_url.rstrip('/')}/collections", timeout=1.0):
            return True
    except (OSError, URLError):
        return False


def collection_readiness(experiment: ExperimentConfig, qdrant_url: str) -> dict:
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=qdrant_url, timeout=1.0)
        info = client.get_collection(experiment.collection)
    except Exception as error:  # noqa: BLE001  # pragma: no cover
        return {"ready": False, "error": str(error)}
    errors = []
    if str(getattr(info.status, "value", info.status)).lower().split(".")[-1] != "green":
        errors.append(f"status is {info.status}")
    if info.points_count != experiment.dataset.records:
        errors.append(f"points expected {experiment.dataset.records}, found {info.points_count}")
    vector_config = info.config.params.vectors
    if vector_config.size != experiment.model.dimension:
        errors.append(f"dimension expected {experiment.model.dimension}, found {vector_config.size}")
    return {
        "ready": not errors,
        "error": "; ".join(errors) if errors else None,
        "report": {
            "collection": experiment.collection,
            "points": info.points_count,
            "dimension": vector_config.size,
            "status": str(getattr(info.status, "value", info.status)).lower().split(".")[-1],
        },
    }


def find_experiment(
    dataset_id: str,
    model_id: str,
    *,
    root: Path | None = None,
) -> ExperimentConfig:
    for experiment in load_app_experiments(root):
        if experiment.dataset.id == dataset_id and experiment.model.id == model_id:
            return experiment
    raise KeyError(f"No experiment is configured for dataset={dataset_id!r}, model={model_id!r}")


def find_dataset(dataset_id: str, *, root: Path | None = None) -> DatasetConfig:
    for experiment in load_app_experiments(root):
        if experiment.dataset.id == dataset_id:
            return experiment.dataset
    raise KeyError(f"No dataset is configured with id={dataset_id!r}")


def constraint_options(dataset: DatasetConfig, data_dir: Path) -> list[dict]:
    path = data_dir / dataset.filename
    return _constraint_options(
        str(path.resolve()),
        dataset.relevance_fields,
        str(data_dir.resolve().parent),
    )


@lru_cache(maxsize=16)
def _constraint_options(path: str, relevance_fields: tuple[str, ...], root: str) -> list[dict]:
    counts: Counter[str] = Counter()
    for record in iter_entity_cards(Path(path)):
        values = set()
        for field in relevance_fields:
            raw = record.get(field, [])
            if isinstance(raw, list):
                values.update(str(item) for item in raw)
        counts.update(values)
    definitions = ontology_definitions(Path(root))
    return [
        _constraint_option(value, count, definitions.get(value))
        for value, count in sorted(
            counts.items(),
            key=lambda item: (compact_type_label(item[0]).lower(), item[0]),
        )
    ]


def _constraint_option(value: str, count: int, definition: dict | None) -> dict:
    label = (definition or {}).get("label") or compact_type_label(value)
    comment = (definition or {}).get("definition")
    if comment:
        tooltip = f"{comment}\nURI: {value}. Matching records: {count}."
    else:
        tooltip = (
            "No ontology definition was found in the available TTL files. "
            f"URI: {value}. Matching records: {count}."
        )
    return {
        "value": value,
        "uri": value,
        "label": label,
        "count": count,
        "display": f"{label} ({count})",
        "definition": comment,
        "tooltip": tooltip,
    }


@lru_cache(maxsize=8)
def ontology_definitions(root: Path) -> dict[str, dict[str, str]]:
    definitions: dict[str, dict[str, str]] = {}
    for path in _ontology_paths(root):
        definitions.update(_parse_ttl_annotations(path))
    return definitions


def _ontology_paths(root: Path) -> tuple[Path, ...]:
    search_roots = (root, root.parent, root / "ontologies", root / "ontology", root / "ttl")
    paths = []
    seen = set()
    for search_root in search_roots:
        if not search_root.is_dir():
            continue
        for path in sorted(search_root.glob("*.ttl")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            paths.append(resolved)
    return tuple(paths)


def _parse_ttl_annotations(path: Path) -> dict[str, dict[str, str]]:
    prefixes: dict[str, str] = {}
    blocks: list[tuple[str, str]] = []
    subject: str | None = None
    block_lines: list[str] = []

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        prefix_match = re.match(r"@prefix\s+([^:]*):\s+<([^>]+)>\s+\.", stripped)
        if prefix_match:
            prefixes[prefix_match.group(1)] = prefix_match.group(2)
            continue
        if subject is None:
            if stripped.startswith("@"):
                continue
            subject = stripped
            block_lines = []
            continue
        if stripped == ".":
            blocks.append((subject, "\n".join(block_lines)))
            subject = None
            block_lines = []
            continue
        block_lines.append(stripped)

    annotations = {}
    for raw_subject, block in blocks:
        uri = _expand_ttl_name(raw_subject, prefixes)
        if not uri:
            continue
        comment = _ttl_literal(block, "rdfs:comment")
        label = _ttl_literal(block, "rdfs:label")
        if comment or label:
            annotations[uri] = {
                "definition": comment or "",
                "label": label or compact_type_label(uri),
            }
    return annotations


def _expand_ttl_name(value: str, prefixes: dict[str, str]) -> str | None:
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    if ":" not in value:
        return None
    prefix, local = value.split(":", 1)
    namespace = prefixes.get(prefix)
    if not namespace:
        return None
    return namespace + local


def _ttl_literal(block: str, predicate: str) -> str | None:
    match = re.search(rf"{re.escape(predicate)}\s+(\"(?:\\.|[^\"\\])*\")", block)
    if not match:
        return None
    try:
        value = ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError):
        return match.group(1).strip('"')
    return " ".join(str(value).split())
