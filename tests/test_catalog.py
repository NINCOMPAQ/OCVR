import json
from pathlib import Path

from ontology_retrieval.catalog import (
    DEFAULT_DATASET_ID,
    DEFAULT_MODEL_ID,
    build_catalog,
    compact_type_label,
    constraint_options,
)
from ontology_retrieval.config import DatasetConfig

ROOT = Path(__file__).parents[1]


def test_catalog_deduplicates_dataset_model_pairs():
    catalog = build_catalog(root=ROOT, include_readiness=False)

    assert len(catalog["datasets"]) == 3
    assert len(catalog["models"]) == 2
    assert catalog["defaults"] == {
        "dataset_id": DEFAULT_DATASET_ID,
        "model_id": DEFAULT_MODEL_ID,
    }
    pairs = {
        (experiment["dataset_id"], experiment["model_id"]) for experiment in catalog["experiments"]
    }
    assert len(pairs) == 6
    assert len(catalog["experiments"]) == 6
    assert any(model["id"] == DEFAULT_MODEL_ID and model["default"] for model in catalog["models"])


def test_compact_type_label_handles_hash_and_path_uris():
    assert (
        compact_type_label("https://example.test/onto#AirspaceRouteSegment")
        == "AirspaceRouteSegment"
    )
    assert compact_type_label("http://dbpedia.org/ontology/PopulatedPlace") == "PopulatedPlace"


def test_constraint_options_count_records_across_relevance_fields(tmp_path):
    data = tmp_path / "fixture.jsonl"
    rows = [
        {
            "iri": "urn:one",
            "card_text": "One",
            "types": ["urn:Target"],
            "types_closure": ["urn:Target", "urn:Thing"],
        },
        {
            "iri": "urn:two",
            "card_text": "Two",
            "types": ["urn:Other"],
            "types_closure": ["urn:Thing"],
        },
    ]
    data.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    dataset = DatasetConfig(
        id="fixture",
        filename=data.name,
        records=2,
        bytes=data.stat().st_size,
        sha256="unused",
        artifact_url=None,
        text_field="card_text",
        payload_fields=("types", "types_closure"),
        relevance_fields=("types_closure", "types"),
        benchmark=tmp_path / "benchmark.json",
    )

    options = {item["uri"]: item for item in constraint_options(dataset, tmp_path)}

    assert options["urn:Target"]["count"] == 1
    assert options["urn:Thing"]["count"] == 2
    assert options["urn:Target"]["label"] == "Target"
    assert options["urn:Target"]["definition"] is None
    assert "URI: urn:Target" in options["urn:Target"]["tooltip"]


def test_constraint_options_use_ttl_comments_and_labels(tmp_path):
    data_dir = tmp_path / "datasets"
    data_dir.mkdir()
    data = data_dir / "fixture.jsonl"
    target = "https://example.test/onto#TargetClass"
    data.write_text(
        json.dumps(
            {
                "iri": "urn:one",
                "card_text": "One",
                "types": [target],
                "types_closure": [target],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "ontology.ttl").write_text(
        """@prefix ex: <https://example.test/onto#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:TargetClass
  rdf:type owl:Class ;
  rdfs:comment "Definition from the ontology file." ;
  rdfs:label "Target class" ;
.
""",
        encoding="utf-8",
    )
    dataset = DatasetConfig(
        id="fixture",
        filename=data.name,
        records=1,
        bytes=data.stat().st_size,
        sha256="unused",
        artifact_url=None,
        text_field="card_text",
        payload_fields=("types", "types_closure"),
        relevance_fields=("types_closure", "types"),
        benchmark=tmp_path / "benchmark.json",
    )

    [option] = constraint_options(dataset, data_dir)

    assert option["label"] == "Target class"
    assert option["definition"] == "Definition from the ontology file."
    assert "Definition from the ontology file." in option["tooltip"]
