import json

import pytest

from ontology_retrieval.assemble import ORDER, assemble_runs


def _write_run(path, dataset, model):
    summary = []
    for strategy, limit in [
        ("unconstrained", 5),
        ("pre-hoc", 5),
        ("post-hoc", 25),
        ("post-hoc", 100),
        ("post-hoc", 200),
        ("post-hoc", 400),
        ("post-hoc", 2000),
    ]:
        summary.append(
            {
                "strategy": strategy,
                "retrieval_limit": limit,
                "valid_at_5": 1.0,
                "success_at_5": 1.0,
                "time_seconds": 0.1,
                "examined": limit,
            }
        )
    path.write_text(
        json.dumps({"dataset": dataset, "model": model, "summary": summary}), encoding="utf-8"
    )


def test_assemble_requires_complete_six_run_matrix(tmp_path):
    paths = []
    for index, (dataset, model) in enumerate(ORDER):
        path = tmp_path / f"{index}.json"
        _write_run(path, dataset, model)
        paths.append(path)
    result = assemble_runs(paths)
    assert len(result["rows"]) == 42


def test_assemble_rejects_missing_run(tmp_path):
    dataset, model = next(iter(ORDER))
    path = tmp_path / "one.json"
    _write_run(path, dataset, model)
    with pytest.raises(ValueError, match="Missing experiment"):
        assemble_runs([path])
