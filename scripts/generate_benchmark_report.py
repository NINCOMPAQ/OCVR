from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean


DATASET_NAMES = {
    "atmonto-enriched-v1": "ATMONTO",
    "brick-mortardata-enriched-v1": "Brick",
    "dbpedia-us-civic-places-enriched-v1": "DBpedia US Civic Geography",
}
DATASET_ORDER = {name: index for index, name in enumerate(DATASET_NAMES)}
MODEL_FILES = {
    "all-MiniLM-L6-v2": "minilm",
    "bge-large-en-v1.5": "bge",
}
STRATEGY_NAMES = {
    "unconstrained": "Unconstrained",
    "pre-hoc": "Pre-hoc",
    "post-hoc": "Post-hoc",
}
STRATEGY_ORDER = {name: index for index, name in enumerate(STRATEGY_NAMES)}
FIELDS = ["dataset", "method", "cap", "valid_at_5", "success_at_5", "score", "time_seconds"]


def load_runs(paths: list[Path]) -> list[dict]:
    runs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    expected = {(dataset, model) for dataset in DATASET_NAMES for model in MODEL_FILES}
    actual = {(run["dataset"], run["model"]) for run in runs}
    if len(runs) != 6 or actual != expected:
        raise ValueError(
            "Expected one run for each dataset/model pair; "
            f"missing={expected-actual}, extra={actual-expected}"
        )
    if any(run.get("queries") != 50 for run in runs):
        raise ValueError("Every benchmark run must contain exactly 50 queries")
    return runs


def detailed_rows(runs: list[dict], model: str) -> list[dict]:
    rows = []
    for run in runs:
        if run["model"] != model:
            continue
        for value in run["summary"]:
            rows.append(_row(DATASET_NAMES[run["dataset"]], value))
    rows.sort(
        key=lambda row: (
            DATASET_ORDER[_dataset_id(row["dataset"])],
            STRATEGY_ORDER[_strategy_id(row["method"])],
            row["cap"],
        )
    )
    return rows


def average_rows(runs: list[dict], model: str) -> list[dict]:
    groups = defaultdict(list)
    for run in runs:
        if run["model"] == model:
            for value in run["summary"]:
                groups[(value["strategy"], value["retrieval_limit"])].append(value)
    rows = []
    for (strategy, cap), values in groups.items():
        if len(values) != 3:
            raise ValueError(f"Expected three datasets for {(model, strategy, cap)}")
        rows.append(
            {
                "dataset": "Average across datasets",
                "method": STRATEGY_NAMES[strategy],
                "cap": cap,
                "valid_at_5": mean(value["valid_at_5"] for value in values),
                "success_at_5": mean(value["success_at_5"] for value in values),
                "score": mean(value["mean_score"] for value in values),
                "time_seconds": mean(value["time_seconds"] for value in values),
            }
        )
    rows.sort(key=lambda row: (STRATEGY_ORDER[_strategy_id(row["method"])], row["cap"]))
    return rows


def _row(dataset: str, value: dict) -> dict:
    return {
        "dataset": dataset,
        "method": STRATEGY_NAMES[value["strategy"]],
        "cap": value["retrieval_limit"],
        "valid_at_5": value["valid_at_5"],
        "success_at_5": value["success_at_5"],
        "score": value["mean_score"],
        "time_seconds": value["time_seconds"],
    }


def _dataset_id(display: str) -> str:
    return next(key for key, value in DATASET_NAMES.items() if value == display)


def _strategy_id(display: str) -> str:
    return next(key for key, value in STRATEGY_NAMES.items() if value == display)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "valid_at_5": f"{row['valid_at_5']:.4f}",
                    "success_at_5": f"{row['success_at_5']:.4f}",
                    "score": f"{row['score']:.4f}",
                    "time_seconds": f"{row['time_seconds']:.4f}",
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate dataset-level and averaged benchmark-result CSVs"
    )
    parser.add_argument("runs", type=Path, nargs=6)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    runs = load_runs(args.runs)
    for model, stem in MODEL_FILES.items():
        write_csv(args.output_dir / f"{stem}-by-dataset.csv", detailed_rows(runs, model))
        write_csv(args.output_dir / f"{stem}-average.csv", average_rows(runs, model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
