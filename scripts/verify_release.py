from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from statistics import mean

ROOT = Path(__file__).parents[1]
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MODEL_REVISION = re.compile(r"^[0-9a-f]{40}$")
PRESERVED_RUNS = {
    "atmonto-bge-final-optimized.json": (
        "atmonto-enriched-v1",
        "bge-large-en-v1.5",
        "atmonto.json",
    ),
    "atmonto-minilm-final-optimized.json": (
        "atmonto-enriched-v1",
        "all-MiniLM-L6-v2",
        "atmonto.json",
    ),
    "brick-bge-final-optimized.json": (
        "brick-mortardata-enriched-v1",
        "bge-large-en-v1.5",
        "brick.json",
    ),
    "brick-minilm-final-optimized.json": (
        "brick-mortardata-enriched-v1",
        "all-MiniLM-L6-v2",
        "brick.json",
    ),
    "dbpedia-bge-v2-final-optimized.json": (
        "dbpedia-us-civic-places-enriched-v1",
        "bge-large-en-v1.5",
        "dbpedia-us-civic-places-natural.json",
    ),
    "dbpedia-minilm-v2-final-optimized.json": (
        "dbpedia-us-civic-places-enriched-v1",
        "all-MiniLM-L6-v2",
        "dbpedia-us-civic-places-natural.json",
    ),
}
EXPECTED_RETRIEVAL_ROWS = {
    ("unconstrained", 5),
    ("pre-hoc", 5),
    ("post-hoc", 25),
    ("post-hoc", 100),
    ("post-hoc", 200),
    ("post-hoc", 400),
    ("post-hoc", 2000),
}
DATASET_NAMES = {
    "atmonto-enriched-v1": "ATMONTO",
    "brick-mortardata-enriched-v1": "Brick",
    "dbpedia-us-civic-places-enriched-v1": "DBpedia US Civic Geography",
}
MODEL_STEMS = {"all-MiniLM-L6-v2": "minilm", "bge-large-en-v1.5": "bge"}
STRATEGY_NAMES = {
    "unconstrained": "Unconstrained",
    "pre-hoc": "Pre-hoc",
    "post-hoc": "Post-hoc",
}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def verify_preserved_sources(errors: list[str]) -> None:
    source_root = ROOT / "provenance" / "source-inputs"
    manifests = {
        "atmonto.json": source_root / "atmonto",
        "brick.json": source_root / "brick",
    }
    for manifest_name, base in manifests.items():
        manifest_path = ROOT / "configs" / "sources" / manifest_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["files"]:
            source_name = Path(item["path"])
            if manifest_name == "brick.json" and source_name.parent.name:
                source_name = Path("mortardata-models") / source_name.name
            path = base / source_name
            if not path.is_file():
                errors.append(f"Missing preserved source input: {path}")
                continue
            if path.stat().st_size != item["bytes"]:
                errors.append(f"{path}: byte size does not match its source manifest")
            if sha256_file(path) != item["sha256"]:
                errors.append(f"{path}: SHA-256 does not match its source manifest")


def verify_artifact_checksums(errors: list[str]) -> None:
    base = ROOT / "provenance" / "final-experiment-artifacts"
    manifest_path = base / "checksums.sha256"
    expected_names = {
        "dataset_characterization.json",
        "dataset_characterization.md",
        *(f"per-query-results/{name}" for name in PRESERVED_RUNS),
    }
    if not manifest_path.is_file():
        errors.append(f"Missing preservation checksum manifest: {manifest_path}")
        return
    entries: dict[str, str] = {}
    for line_number, line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            digest, name = line.split(maxsplit=1)
        except ValueError:
            errors.append(f"{manifest_path}:{line_number}: malformed checksum entry")
            continue
        relative = PurePosixPath(name.lstrip("*"))
        if not SHA256.fullmatch(digest) or relative.is_absolute() or ".." in relative.parts:
            errors.append(f"{manifest_path}:{line_number}: invalid checksum entry")
            continue
        key = relative.as_posix()
        if key in entries:
            errors.append(f"{manifest_path}:{line_number}: duplicate path {key}")
        entries[key] = digest
    if set(entries) != expected_names:
        errors.append(
            f"{manifest_path}: artifact set mismatch; "
            f"missing={sorted(expected_names - set(entries))}, "
            f"extra={sorted(set(entries) - expected_names)}"
        )
    for name, digest in entries.items():
        path = base / name
        if not path.is_file():
            errors.append(f"Missing preserved experiment artifact: {path}")
        elif sha256_file(path) != digest:
            errors.append(f"{path}: SHA-256 does not match preservation manifest")


def _metric_row(dataset: str, summary: dict) -> dict[str, str]:
    return {
        "dataset": dataset,
        "method": STRATEGY_NAMES[summary["strategy"]],
        "cap": str(summary["retrieval_limit"]),
        "valid_at_5": f"{summary['valid_at_5']:.4f}",
        "success_at_5": f"{summary['success_at_5']:.4f}",
        "score": f"{summary['mean_score']:.4f}",
        "time_seconds": f"{summary['time_seconds']:.4f}",
    }


def _compare_csv(path: Path, expected: list[dict[str, str]], errors: list[str]) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        actual = list(csv.DictReader(handle))
    key = lambda row: (row["dataset"], row["method"], row["cap"])
    if {key(row): row for row in actual} != {key(row): row for row in expected}:
        errors.append(f"{path}: values do not match the preserved per-query runs")


def verify_preserved_runs(errors: list[str]) -> None:
    base = ROOT / "provenance" / "final-experiment-artifacts" / "per-query-results"
    runs = []
    for name, (dataset, model, benchmark_name) in PRESERVED_RUNS.items():
        path = base / name
        if not path.is_file():
            errors.append(f"Missing preserved per-query run: {path}")
            continue
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"Cannot read preserved per-query run {path}: {error}")
            continue
        runs.append(run)
        if run.get("schema_version") != 2:
            errors.append(f"{path}: expected schema version 2")
        if (run.get("dataset"), run.get("model")) != (dataset, model):
            errors.append(f"{path}: dataset/model identity does not match its filename")
        benchmark = json.loads((ROOT / "benchmarks" / benchmark_name).read_text(encoding="utf-8"))
        expected_query_ids = {row["id"] for row in benchmark}
        if run.get("queries") != len(expected_query_ids):
            errors.append(f"{path}: expected {len(expected_query_ids)} queries")
        summary = run.get("summary", [])
        summary_rows = {(row.get("strategy"), row.get("retrieval_limit")) for row in summary}
        if summary_rows != EXPECTED_RETRIEVAL_ROWS or len(summary) != len(summary_rows):
            errors.append(f"{path}: summary strategy/cap coverage is incomplete or duplicated")
        results = run.get("results", [])
        if len(results) != len(expected_query_ids) * len(EXPECTED_RETRIEVAL_ROWS):
            errors.append(f"{path}: unexpected number of per-query result rows")
        coverage: dict[str, set[tuple[str, int]]] = defaultdict(set)
        for row in results:
            coverage[row.get("query_id")].add((row.get("strategy"), row.get("retrieval_limit")))
        if set(coverage) != expected_query_ids:
            errors.append(f"{path}: result query IDs do not match the benchmark")
        if any(rows != EXPECTED_RETRIEVAL_ROWS for rows in coverage.values()):
            errors.append(f"{path}: one or more queries have incomplete strategy/cap coverage")

    pairs = {(run.get("dataset"), run.get("model")) for run in runs}
    expected_pairs = {(dataset, model) for dataset in DATASET_NAMES for model in MODEL_STEMS}
    if len(runs) != 6 or pairs != expected_pairs:
        errors.append("Preserved runs do not contain exactly one dataset/model pair each")
        return
    for model, stem in MODEL_STEMS.items():
        matching = [run for run in runs if run["model"] == model]
        detailed = [
            _metric_row(DATASET_NAMES[run["dataset"]], row)
            for run in matching
            for row in run["summary"]
        ]
        _compare_csv(ROOT / "results" / "benchmark" / f"{stem}-by-dataset.csv", detailed, errors)
        grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
        for run in matching:
            for row in run["summary"]:
                grouped[(row["strategy"], row["retrieval_limit"])].append(row)
        averages = []
        for (strategy, cap), rows in grouped.items():
            averages.append(
                _metric_row(
                    "Average across datasets",
                    {
                        "strategy": strategy,
                        "retrieval_limit": cap,
                        "valid_at_5": mean(row["valid_at_5"] for row in rows),
                        "success_at_5": mean(row["success_at_5"] for row in rows),
                        "mean_score": mean(row["mean_score"] for row in rows),
                        "time_seconds": mean(row["time_seconds"] for row in rows),
                    },
                )
            )
        _compare_csv(ROOT / "results" / "benchmark" / f"{stem}-average.csv", averages, errors)


def verify_figure_pdf(errors: list[str]) -> None:
    path = ROOT / "results" / "benchmark" / "valid-at-5-by-candidate-limit.pdf"
    if not path.is_file():
        return
    content = path.read_bytes()
    if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-1024:]:
        errors.append(f"{path}: malformed or truncated PDF")
    if b"/Subtype /Type3" in content:
        errors.append(f"{path}: contains a Type 3 font")
    if b"/Subtype /Type0" not in content or b"/FontFile2" not in content:
        errors.append(f"{path}: expected an embedded TrueType/CID font")


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
                content_hash = sha256_file(dataset_path)
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
    verify_preserved_sources(errors)

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
    verify_artifact_checksums(errors)
    verify_preserved_runs(errors)
    verify_figure_pdf(errors)

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
