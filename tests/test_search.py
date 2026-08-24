from pathlib import Path
from types import SimpleNamespace

from ontology_retrieval.search import SearchService

ROOT = Path(__file__).parents[1]
TARGET = "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment"


class FakeModel:
    def encode(self, queries, normalize_embeddings):
        assert queries == ["arrival route segment near Newark"]
        assert normalize_embeddings is True
        return [[0.1] * 384]


class FakeClient:
    def __init__(self):
        self.calls = []
        self.points = [
            SimpleNamespace(
                id="one",
                score=0.91,
                payload={
                    "iri": "urn:one",
                    "label": "Route one",
                    "types_closure": [TARGET],
                    "types": [TARGET],
                },
            ),
            SimpleNamespace(
                id="two",
                score=0.82,
                payload={
                    "iri": "urn:two",
                    "label": "Weather",
                    "types_closure": ["urn:Other"],
                    "types": ["urn:Other"],
                },
            ),
            SimpleNamespace(
                id="three",
                score=0.77,
                payload={
                    "iri": "urn:three",
                    "label": "Route three",
                    "types_closure": [TARGET],
                    "types": [TARGET],
                },
            ),
        ]

    def query_points(self, collection_name, query, limit, with_payload, query_filter=None):
        self.calls.append(
            {
                "collection": collection_name,
                "limit": limit,
                "filter": query_filter,
            }
        )
        points = self.points
        if query_filter is not None:
            points = [point for point in points if TARGET in point.payload.get("types_closure", [])]
        return SimpleNamespace(points=points[:limit])


def test_search_runs_unconstrained_prehoc_and_posthoc_modes():
    fake_client = FakeClient()
    service = SearchService(
        root=ROOT,
        qdrant_url="http://qdrant.test",
        client_factory=lambda _url: fake_client,
        model_factory=lambda _experiment: FakeModel(),
        verify_ready=False,
    )

    result = service.run(
        dataset_id="atmonto-enriched-v1",
        model_id="all-MiniLM-L6-v2",
        query="arrival route segment near Newark",
        constraint_uris=[TARGET],
    )

    assert result["collection"] == "atmonto_minilm_enriched"
    assert [group["strategy"] for group in result["results"]] == [
        "unconstrained",
        "pre-hoc",
        "post-hoc",
    ]
    unconstrained, prehoc, posthoc = result["results"]
    assert unconstrained["valid_at_k"] == 0.4
    assert prehoc["hits"][0]["valid"] is True
    assert prehoc["hits"][0]["matched_types"] == [{"uri": TARGET, "label": "AirspaceRouteSegment"}]
    assert posthoc["hits"][0]["payload"]["label"] == "Route one"
    assert len(fake_client.calls) == 3
