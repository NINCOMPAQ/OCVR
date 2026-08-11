# Experiment protocol

The paper compares unconstrained, pre-hoc constrained, and post-hoc constrained vector retrieval for three datasets and two embedding models.

## Paper-v1 behavior

- `top_k` is five.
- Unconstrained retrieval asks Qdrant for five unfiltered neighbors.
- Pre-hoc retrieval asks for five neighbors with a Qdrant type-closure filter.
- Post-hoc retrieval requests growing unfiltered prefixes in increments of 25, locally accepts type-valid points, and stops after five accepted points or the configured cap.
- Post-hoc caps are 25, 100, 200, 400, and 2,000.
- Embeddings are normalized and Qdrant uses cosine distance.

`valid@5` is the number of type-valid results divided by five. Missing result slots count as invalid. `success@5` is one only when all five slots are type-valid, then averaged over queries.

Historical `time` measures Qdrant request wall time and excludes query embedding. It should not be expected to match across hardware or software environments.

## Clarified work measures

New structured results retain three distinct post-hoc quantities:

- `examined`: largest unique rank prefix inspected;
- `requests`: Qdrant requests issued;
- `candidates_transferred`: total hits returned across repeated prefix requests.

This preserves the paper measure while making repeated retrieval work visible.

## Interpretation warning

Pre-hoc type-validity is expected to be perfect when at least five matching entities exist because the retrieval filter and validity test use the same type metadata. It measures constraint satisfaction, not independent semantic relevance.

## Planned benchmark v2

The paper-v1 suites contain 50 ATMONTO queries, 50 Brick queries, and 42 DBpedia queries. The 42-query DBpedia suite must remain unchanged because its denominator is encoded in the published results. A future benchmark-v2 release should add eight reviewed DBpedia queries, bringing that suite to 50 for cross-dataset consistency. The additional queries must receive new stable IDs and be reported as a separate protocol; they must not be inserted silently into paper-v1.
