import json
from pathlib import Path

from ontology_retrieval.config import load_experiment


ROOT = Path(__file__).parents[1]


def test_all_experiments_load():
    model_paths = sorted((ROOT / "configs" / "models").glob("*.json"))
    assert [path.name for path in model_paths] == ["bge-large.json", "minilm.json"]
    paths = sorted((ROOT / "configs" / "experiments").glob("*.json"))
    experiments = [load_experiment(path) for path in paths]
    assert len(experiments) == 6
    assert {item.dataset.id for item in experiments} == {
        "atmonto-enriched-v1",
        "brick-mortardata-enriched-v1",
        "dbpedia-us-civic-places-enriched-v1",
    }
    assert {item.model.dimension for item in experiments} == {384, 1024}


def test_benchmark_counts_match_paper_protocol():
    expected = {
        "atmonto-enriched-v1": 50,
        "brick-mortardata-enriched-v1": 50,
        "dbpedia-us-civic-places-enriched-v1": 50,
    }
    for path in (ROOT / "configs" / "experiments").glob("*.json"):
        experiment = load_experiment(path)
        queries = json.loads(experiment.dataset.benchmark.read_text(encoding="utf-8"))
        assert len(queries) == expected[experiment.dataset.id]
        assert all(
            {"id", "name", "query", "constraint_any"} <= row.keys()
            for row in queries
        )
