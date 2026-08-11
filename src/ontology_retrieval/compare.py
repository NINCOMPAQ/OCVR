from __future__ import annotations

from typing import Any


KEYS = ("ontology", "model", "strategy", "retrieval_limit")
DETERMINISTIC = ("valid_at_5", "success_at_5", "examined")


def compare_master_results(actual: dict[str, Any], expected: dict[str, Any], tolerance: float = 0.00005) -> list[str]:
    expected_rows = {tuple(row[key] for key in KEYS): row for row in expected["rows"]}
    actual_rows = {tuple(row[key] for key in KEYS): row for row in actual["rows"]}
    differences = []
    for key in sorted(set(expected_rows) | set(actual_rows)):
        if key not in actual_rows:
            differences.append(f"missing actual row: {key}")
            continue
        if key not in expected_rows:
            differences.append(f"unexpected actual row: {key}")
            continue
        for metric in DETERMINISTIC:
            observed = float(actual_rows[key][metric])
            baseline = float(expected_rows[key][metric])
            metric_tolerance = 0.005 if metric == "examined" else tolerance
            if abs(observed - baseline) > metric_tolerance:
                differences.append(
                    f"{key} {metric}: expected {baseline}, found {observed}"
                )
    return differences

