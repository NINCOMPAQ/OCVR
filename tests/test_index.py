from ontology_retrieval.index import stable_point_id


def test_point_ids_are_stable_and_dataset_scoped():
    assert stable_point_id("dataset", "urn:one") == stable_point_id("dataset", "urn:one")
    assert stable_point_id("dataset-a", "urn:one") != stable_point_id("dataset-b", "urn:one")

