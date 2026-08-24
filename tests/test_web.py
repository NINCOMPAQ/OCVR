from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx2")

from starlette.testclient import TestClient

from ontology_retrieval.search import SearchService
from ontology_retrieval.web import create_app

ROOT = Path(__file__).parents[1]


def test_catalog_endpoint_returns_defaults():
    client = TestClient(create_app(root=ROOT, qdrant_url="http://qdrant.test"))

    response = client.get("/api/catalog")

    assert response.status_code == 200
    body = response.json()
    assert body["defaults"]["dataset_id"] == "atmonto-enriched-v1"
    assert body["defaults"]["model_id"] == "all-MiniLM-L6-v2"
    assert len(body["experiments"]) == 6


def test_constraints_endpoint_returns_dataset_classes():
    client = TestClient(create_app(root=ROOT, qdrant_url="http://qdrant.test"))

    response = client.get("/api/datasets/atmonto-enriched-v1/constraints")

    assert response.status_code == 200
    values = {item["label"] for item in response.json()["constraints"]}
    assert "AirspaceRouteSegment" in values


def test_search_endpoint_reports_validation_errors():
    service = SearchService(root=ROOT, qdrant_url="http://qdrant.test", verify_ready=False)
    client = TestClient(
        create_app(root=ROOT, qdrant_url="http://qdrant.test", search_service=service)
    )

    response = client.post(
        "/api/search",
        json={
            "dataset_id": "atmonto-enriched-v1",
            "model_id": "all-MiniLM-L6-v2",
            "query": "   ",
            "constraint_uris": [
                "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment"
            ],
        },
    )

    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]
