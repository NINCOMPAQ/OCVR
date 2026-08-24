from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from .assemble import DISPLAY, ORDER

STRATEGY_ORDER = {"unconstrained": 0, "pre-hoc": 1, "post-hoc": 2}


def average_runs(paths: list[Path]) -> list[dict]:
    runs = []
    seen = set()
    for path in paths:
        run = json.loads(path.read_text(encoding="utf-8"))
        key = (run["dataset"], run["model"])
        if key not in ORDER:
            raise ValueError(f"Unexpected dataset/model pair in {path}: {key}")
        if key in seen:
            raise ValueError(f"Duplicate dataset/model pair: {key}")
        seen.add(key)
        runs.append(run)
    missing = set(ORDER) - seen
    if missing:
        raise ValueError(f"Missing experiment runs: {sorted(missing)}")

    groups = defaultdict(list)
    for run in runs:
        for summary in run["summary"]:
            key = (run["model"], summary["strategy"], summary["retrieval_limit"])
            groups[key].append(summary)

    rows = []
    for (model, strategy, cap), values in groups.items():
        if len(values) != 3:
            raise ValueError(
                f"Expected three datasets for {(model, strategy, cap)}, found {len(values)}"
            )
        rows.append(
            {
                "model": DISPLAY[model],
                "method": DISPLAY[strategy],
                "cap": cap,
                "valid_at_5": mean(value["valid_at_5"] for value in values),
                "success_at_5": mean(value["success_at_5"] for value in values),
                "score": mean(value["mean_score"] for value in values),
                "time_seconds": mean(value["time_seconds"] for value in values),
            }
        )
    rows.sort(
        key=lambda row: (
            0 if row["model"] == "all-MiniLM-L6-v2" else 1,
            STRATEGY_ORDER[row["method"].lower()],
            row["cap"],
        )
    )
    if len(rows) != 14:
        raise ValueError(f"Expected 14 averaged rows, found {len(rows)}")
    return rows


def write_average_csv(rows: list[dict], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = ["model", "method", "cap", "valid_at_5", "success_at_5", "score", "time_seconds"]
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "model": row["model"],
                    "method": row["method"],
                    "cap": row["cap"],
                    "valid_at_5": f"{row['valid_at_5']:.4f}",
                    "success_at_5": f"{row['success_at_5']:.4f}",
                    "score": f"{row['score']:.4f}",
                    "time_seconds": f"{row['time_seconds']:.4f}",
                }
            )
