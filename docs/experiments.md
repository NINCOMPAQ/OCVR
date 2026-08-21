# Experiment protocol

The paper compares unconstrained, pre-hoc ontology-constrained, and post-hoc ontology-filtered vector retrieval across three datasets and two embedding models.

## Benchmark behavior

- `top_k` is five.
- Unconstrained retrieval asks Qdrant for five unfiltered neighbors.
- Pre-hoc retrieval asks for five neighbors with a Qdrant type-closure filter.
- Post-hoc retrieval requests growing unfiltered prefixes in increments of 25, locally accepts type-valid points, and stops after five accepted points or the configured cap.
- Post-hoc caps are 25, 100, 200, 400, and 2,000.
- Embeddings are normalized and Qdrant uses cosine distance.

`valid@5` is the number of type-valid results divided by five. Missing result slots count as invalid. `success@5` is one only when all five slots are type-valid, then averaged over queries.

Retrieval `time` measures Qdrant request wall time and excludes query embedding. Exact timing is environment dependent.

## Work measures

Structured evaluator outputs retain three distinct post-hoc quantities:

- `examined`: largest unique rank prefix inspected;
- `requests`: Qdrant requests issued;
- `candidates_transferred`: total hits returned across repeated prefix requests.

Result schema version 2 also retains the natural-language query, requested type constraint, and final ranked hits for every query/strategy/cap row. Each hit records its rank, Qdrant point ID, similarity score, type-valid flag, and returned payload. Post-hoc rows contain the accepted type-valid result list; `examined` and `candidates_transferred` describe the broader candidate search needed to produce it.

## Benchmark coverage

The evaluation uses 50 ATMONTO queries, 50 Brick queries, and 50 DBpedia queries. The canonical query files are:

- `benchmarks/atmonto.json`
- `benchmarks/brick.json`
- `benchmarks/dbpedia-us-civic-places-natural.json`

The six experiment configurations are the two embedding-model configurations for each dataset under `configs/experiments/`.

The macro-average results use an unweighted arithmetic mean across the three dataset summaries, so each ontology contributes one third of an average row. Recorded summaries are in `results/benchmark/`.

## Interpretation note

Pre-hoc type validity is expected to be perfect when at least five matching entities exist because the retrieval filter and validity test use the same ontology-type metadata. It measures constraint satisfaction, not independent semantic relevance.

## Indexing configuration

All benchmark collections use HNSW with `m=16`, `ef_construct=100`, and `full_scan_threshold=1000` KB. Qdrant optimizer settings use `indexing_threshold=1000` KB and `default_segment_number=1`; vector quantization is disabled. The `types` and `types_closure` fields are indexed as keyword payload fields.

If indexing is interrupted after Qdrant has accepted some batches, rerun the same index command with `--resume`. The indexer checks collection dimension, distance, and maximum point count, discovers stable IDs already present, and embeds only missing entity cards. `--resume` and `--replace` are mutually exclusive.

Clean-build validation of all six collections is recorded in `results/clean-build-validation.md`. Retrieval calls do not supply explicit `exact`, `hnsw_ef`, or quantization search parameters.
