from __future__ import annotations

import json
from pathlib import Path


DISPLAY = {
    "atmonto-enriched-v1": "ATMONTO",
    "brick-mortardata-enriched-v1": "Brick",
    "dbpedia-us-civic-places-enriched-v1": "DBpedia US Civic Geography",
    "all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "bge-large-en-v1.5": "bge-large-en-v1.5",
    "unconstrained": "Unconstrained",
    "pre-hoc": "Pre-hoc",
    "post-hoc": "Post-hoc",
}

ORDER = {
    ("atmonto-enriched-v1", "all-MiniLM-L6-v2"): 0,
    ("atmonto-enriched-v1", "bge-large-en-v1.5"): 1,
    ("brick-mortardata-enriched-v1", "all-MiniLM-L6-v2"): 2,
    ("brick-mortardata-enriched-v1", "bge-large-en-v1.5"): 3,
    ("dbpedia-us-civic-places-enriched-v1", "all-MiniLM-L6-v2"): 4,
    ("dbpedia-us-civic-places-enriched-v1", "bge-large-en-v1.5"): 5,
}


def assemble_runs(paths: list[Path]) -> dict:
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
    rows = []
    for run in sorted(runs, key=lambda item: ORDER[(item["dataset"], item["model"])]):
        for summary in run["summary"]:
            rows.append(
                {
                    "ontology": DISPLAY[run["dataset"]],
                    "model": DISPLAY[run["model"]],
                    "strategy": DISPLAY[summary["strategy"]],
                    "retrieval_limit": summary["retrieval_limit"],
                    "valid_at_5": summary["valid_at_5"],
                    "success_at_5": summary["success_at_5"],
                    "time_seconds": summary["time_seconds"],
                    "examined": summary["examined"],
                }
            )
    if len(rows) != 42:
        raise ValueError(f"Expected 42 aggregate rows, found {len(rows)}")
    return {"schema_version": 1, "protocol": "paper-v1", "status": "reproduced", "rows": rows}

