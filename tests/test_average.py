import json

import pytest

from ontology_retrieval.assemble import ORDER
from ontology_retrieval.average import average_runs, write_average_csv


def _runs(tmp_path):
    paths = []
    for index, (dataset, model) in enumerate(ORDER):
        path = tmp_path / f"run-{index}.json"
        path.write_text(
            json.dumps(
                {
                    "dataset": dataset,
                    "model": model,
                    "summary": [
                        {
                            "strategy": "unconstrained",
                            "retrieval_limit": 5,
                            "valid_at_5": index / 10,
                            "success_at_5": index / 20,
                            "mean_score": index / 5,
                            "time_seconds": index / 100,
                        },
                        {
                            "strategy": "pre-hoc",
                            "retrieval_limit": 5,
                            "valid_at_5": 1,
                            "success_at_5": 1,
                            "mean_score": index / 5,
                            "time_seconds": index / 100,
                        },
                        *[
                            {
                                "strategy": "post-hoc",
                                "retrieval_limit": cap,
                                "valid_at_5": index / 10,
                                "success_at_5": index / 20,
                                "mean_score": index / 5,
                                "time_seconds": index / 100,
                            }
                            for cap in (25, 100, 200, 400, 2000)
                        ],
                    ],
                }
            ),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def test_average_runs_and_write_csv(tmp_path):
    rows = average_runs(_runs(tmp_path))
    assert len(rows) == 14
    assert rows[0]["model"] == "all-MiniLM-L6-v2"
    assert rows[0]["method"] == "Unconstrained"
    assert rows[0]["valid_at_5"] == pytest.approx(0.2)
    destination = tmp_path / "average.csv"
    write_average_csv(rows, destination)
    assert "all-MiniLM-L6-v2,Unconstrained,5,0.2000" in destination.read_text()


def test_average_runs_requires_six_dataset_model_pairs(tmp_path):
    with pytest.raises(ValueError, match="Missing experiment runs"):
        average_runs(_runs(tmp_path)[:-1])
