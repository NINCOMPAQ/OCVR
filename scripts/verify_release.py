from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MODEL_REVISION = re.compile(r"^[0-9a-f]{40}$")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-unpublished-data", action="store_true")
    args = parser.parse_args(argv)
    errors: list[str] = []
    warnings: list[str] = []

    datasets = []
    for path in sorted((ROOT / "configs" / "datasets").glob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        datasets.append(item)
        if not SHA256.fullmatch(item["sha256"]):
            errors.append(f"{path}: invalid SHA-256")
        if not item.get("artifact_url") and not item.get("included_in_repository"):
            message = f"{path}: dataset is neither included nor available from an artifact URL"
            (warnings if args.allow_unpublished_data else errors).append(message)
        if item.get("included_in_repository"):
            dataset_path = ROOT / "datasets" / item["filename"]
            if not dataset_path.is_file():
                errors.append(f"{path}: included dataset is missing: {dataset_path}")
            else:
                content_hash = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
                if dataset_path.stat().st_size != item["bytes"]:
                    errors.append(f"{dataset_path}: byte size does not match its manifest")
                if content_hash != item["sha256"]:
                    errors.append(f"{dataset_path}: SHA-256 does not match its manifest")
    if len(datasets) != 3:
        errors.append(f"Expected 3 dataset configs, found {len(datasets)}")

    models = []
    for path in sorted((ROOT / "configs" / "models").glob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        models.append(item)
        if not MODEL_REVISION.fullmatch(item.get("revision", "")):
            errors.append(f"{path}: model revision is not a pinned 40-character commit")
        if not item.get("source_url", "").startswith("https://"):
            errors.append(f"{path}: missing HTTPS source URL")
    if len(models) != 2:
        errors.append(f"Expected 2 model configs, found {len(models)}")

    experiments = sorted((ROOT / "configs" / "experiments").glob("*.json"))
    if len(experiments) != 6:
        errors.append(f"Expected 6 experiment configs, found {len(experiments)}")

    sources = list((ROOT / "configs" / "sources").glob("*.json"))
    if len(sources) != 3:
        errors.append(f"Expected 3 source manifests, found {len(sources)}")

    expected_queries = {
        "atmonto.json": 50,
        "brick.json": 50,
        "dbpedia-us-civic-places-natural.json": 50,
    }
    for name, expected in expected_queries.items():
        path = ROOT / "benchmarks" / name
        rows = json.loads(path.read_text(encoding="utf-8"))
        if len(rows) != expected:
            errors.append(f"{name}: expected {expected} queries, found {len(rows)}")
        ids = [row.get("id") for row in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"{name}: duplicate query IDs")

    required_results = [
        "results/benchmark/minilm-average.csv",
        "results/benchmark/minilm-by-dataset.csv",
        "results/benchmark/bge-average.csv",
        "results/benchmark/bge-by-dataset.csv",
        "results/benchmark/valid-at-5-by-candidate-limit.pdf",
    ]
    for name in required_results:
        if not (ROOT / name).is_file():
            errors.append(f"Missing benchmark artifact: {name}")

    legacy_paths = [
        "benchmarks/dbpedia-us-civic-places-v2.json",
        "configs/experiments/dbpedia-minilm-v2.json",
        "configs/experiments/dbpedia-bge-v2.json",
        "results/benchmark-v2",
        "results/final-optimized-rerun",
        "results/paper",
    ]
    for name in legacy_paths:
        if (ROOT / name).exists():
            errors.append(f"Legacy release path should not exist: {name}")

    required = [
        "README.md",
        "CITATION.cff",
        "LICENSE",
        "DATA_LICENSES.md",
        "compose.yaml",
        "pyproject.toml",
    ]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f"Missing required file: {name}")

    release_only = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if "PUBLIC-REPOSITORY-URL-TO-BE-ADDED-BEFORE-RELEASE" in readme:
        release_only.append("README.md still contains the repository URL placeholder")
    if "TODO:" in citation:
        release_only.append("CITATION.cff still contains TODO metadata")
    for message in release_only:
        (warnings if args.allow_unpublished_data else errors).append(message)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Release structure verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
