from ontology_retrieval.render import render_latex


def test_latex_has_six_columns(tmp_path):
    destination = tmp_path / "table.tex"
    render_latex(
        {
            "rows": [
                {
                    "ontology": "Example",
                    "model": "Model",
                    "strategy": "Pre-hoc",
                    "retrieval_limit": 5,
                    "valid_at_5": 1.0,
                    "success_at_5": 1.0,
                    "time_seconds": 0.1,
                    "examined": 5,
                }
            ]
        },
        destination,
    )
    text = destination.read_text(encoding="utf-8")
    assert r"\begin{longtable}{llrrrr}" in text
    assert r"\multicolumn{6}" in text
