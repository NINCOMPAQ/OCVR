from types import SimpleNamespace

import pytest

from ontology_retrieval.index import (
    stable_point_id,
    verify_collection_shape,
    wait_for_collection_ready,
)


def test_point_ids_are_stable_and_dataset_scoped():
    assert stable_point_id("dataset", "urn:one") == stable_point_id("dataset", "urn:one")
    assert stable_point_id("dataset-a", "urn:one") != stable_point_id("dataset-b", "urn:one")


def _experiment(records=10000):
    return SimpleNamespace(
        collection="test_collection",
        model=SimpleNamespace(dimension=384, distance="cosine"),
        dataset=SimpleNamespace(records=records),
    )


def _info(*, indexed=10000, payload_indexes=True):
    schema = SimpleNamespace(data_type="keyword")
    return SimpleNamespace(
        status="green",
        points_count=10000,
        indexed_vectors_count=indexed,
        segments_count=2,
        payload_schema={"types": schema, "types_closure": schema} if payload_indexes else {},
        config=SimpleNamespace(
            params=SimpleNamespace(vectors=SimpleNamespace(size=384, distance="cosine")),
            hnsw_config=SimpleNamespace(
                m=16,
                ef_construct=100,
                full_scan_threshold=1000,
                on_disk=False,
            ),
            optimizer_config=SimpleNamespace(
                default_segment_number=1,
                indexing_threshold=1000,
            ),
        ),
    )


class _Client:
    def __init__(self, states):
        self.states = iter(states)

    def get_collection(self, _name):
        return next(self.states)


def test_readiness_accepts_tail_below_qdrants_indexing_threshold():
    result = wait_for_collection_ready(
        _experiment(), client=_Client([_info(indexed=9333)]), timeout_seconds=0
    )
    assert result["maximum_unindexed_vectors"] == 667


def test_readiness_rejects_tail_above_qdrants_indexing_threshold():
    with pytest.raises(TimeoutError, match="expected at least 9333"):
        wait_for_collection_ready(
            _experiment(), client=_Client([_info(indexed=9332)]), timeout_seconds=0
        )


def test_resume_rejects_missing_payload_indexes():
    with pytest.raises(ValueError, match="missing payload index 'types'"):
        verify_collection_shape(_experiment(), _Client([_info(payload_indexes=False)]))
