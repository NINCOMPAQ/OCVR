from dataclasses import dataclass

from ontology_retrieval.metrics import evaluate_hits, is_relevant


@dataclass
class Hit:
    payload: dict
    score: float


def test_relevance_checks_configured_fields():
    payload = {"types": ["Child"], "types_closure": ["Child", "Parent"]}
    assert is_relevant(payload, ["Parent"], ["types_closure", "types"])
    assert not is_relevant(payload, ["Unrelated"], ["types_closure", "types"])


def test_missing_results_count_as_invalid_at_k():
    hits = [Hit({"types_closure": ["Target"]}, 0.8) for _ in range(3)]
    result = evaluate_hits(hits, ["Target"], ["types_closure"], k=5)
    assert result.relevant_count == 3
    assert result.valid_at_k == 0.6
    assert result.success_at_k == 0.0
    assert result.mean_score == 0.8


def test_success_requires_all_k_results():
    hits = [Hit({"types_closure": ["Target"]}, 0.5) for _ in range(5)]
    result = evaluate_hits(hits, ["Target"], ["types_closure"], k=5)
    assert result.valid_at_k == 1.0
    assert result.success_at_k == 1.0
