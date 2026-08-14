from types import SimpleNamespace

from ontology_retrieval.evaluate import _result
from ontology_retrieval.metrics import evaluate_hits


def test_result_retains_ranked_hits_and_query_context():
    hits = [
        SimpleNamespace(
            id="point-1",
            score=0.75,
            payload={"iri": "urn:one", "label": "One", "types_closure": ["Target"]},
        ),
        SimpleNamespace(
            id="point-2",
            score=0.50,
            payload={"iri": "urn:two", "label": "Two", "types_closure": ["Other"]},
        ),
    ]
    test = {"id": "q001", "query": "find one", "constraint_any": ["Target"]}
    metrics = evaluate_hits(hits, test["constraint_any"], ["types_closure"], 5)

    result = _result(
        test,
        "unconstrained",
        5,
        metrics,
        0.01,
        2,
        1,
        2,
        hits,
        ["types_closure"],
    )

    assert result["query"] == "find one"
    assert result["constraint_any"] == ["Target"]
    assert result["hits"][0] == {
        "rank": 1,
        "point_id": "point-1",
        "score": 0.75,
        "valid": True,
        "payload": {
            "iri": "urn:one",
            "label": "One",
            "types_closure": ["Target"],
        },
    }
    assert result["hits"][1]["rank"] == 2
    assert result["hits"][1]["valid"] is False
