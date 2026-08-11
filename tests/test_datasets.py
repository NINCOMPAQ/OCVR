import hashlib
import json

import pytest

from ontology_retrieval.config import DatasetConfig
from ontology_retrieval.datasets import verify_dataset


def test_verify_dataset_checks_content_and_identity(tmp_path):
    path = tmp_path / "fixture.jsonl"
    content = json.dumps({"iri": "urn:one", "card_text": "One", "types": [], "types_closure": []}) + "\n"
    path.write_text(content, encoding="utf-8")
    encoded = path.read_bytes()
    config = DatasetConfig(
        id="fixture",
        filename=path.name,
        records=1,
        bytes=len(encoded),
        sha256=hashlib.sha256(encoded).hexdigest(),
        artifact_url=None,
        text_field="card_text",
        payload_fields=("types", "types_closure"),
        relevance_fields=("types_closure", "types"),
        benchmark=tmp_path / "queries.json",
    )
    assert verify_dataset(path, config).records == 1


def test_verify_dataset_rejects_duplicate_iris(tmp_path):
    path = tmp_path / "fixture.jsonl"
    row = {"iri": "urn:one", "card_text": "One", "types": [], "types_closure": []}
    content = json.dumps(row) + "\n" + json.dumps(row) + "\n"
    path.write_text(content, encoding="utf-8")
    config = DatasetConfig("fixture", path.name, 2, len(content.encode()), "unused", None, "card_text", ("types", "types_closure"), ("types_closure",), tmp_path / "queries.json")
    with pytest.raises(ValueError, match="Duplicate IRI"):
        verify_dataset(path, config)
