from ontology_retrieval.compare import compare_master_results


def test_compare_ignores_timing_but_checks_metrics():
    row = {
        "ontology": "O",
        "model": "M",
        "strategy": "S",
        "retrieval_limit": 5,
        "valid_at_5": 1.0,
        "success_at_5": 1.0,
        "examined": 5,
        "time_seconds": 1.0,
    }
    expected = {"rows": [row]}
    actual_row = dict(row, time_seconds=99.0)
    assert compare_master_results({"rows": [actual_row]}, expected) == []
    actual_row["valid_at_5"] = 0.8
    assert "valid_at_5" in compare_master_results({"rows": [actual_row]}, expected)[0]
