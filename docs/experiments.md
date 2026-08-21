# Experiment protocol

The submitted paper compares unconstrained, pre-hoc ontology-constrained, and post-hoc ontology-filtered vector retrieval across three datasets and two embedding models.

## Submitted benchmark behavior

- `top_k` is five.
- Unconstrained retrieval asks Qdrant for five unfiltered neighbors.
- Pre-hoc retrieval asks for five neighbors with a Qdrant type-closure filter.
- Post-hoc retrieval requests growing unfiltered prefixes in increments of 25, locally accepts type-valid points, and stops after five accepted points or the configured cap.
- Post-hoc caps are 25, 100, 200, 400, and 2,000.
- Embeddings are normalized and Qdrant uses cosine distance.

`valid@5` is the number of type-valid results divided by five. Missing result slots count as invalid. `success@5` is one only when all five slots are type-valid, then averaged over queries.

Historical `time` measures Qdrant request wall time and excludes query embedding. It should not be expected to match exactly across hardware or software environments.

## Work measures

Structured results retain three distinct post-hoc quantities:

- `examined`: largest unique rank prefix inspected;
- `requests`: Qdrant requests issued;
- `candidates_transferred`: total hits returned across repeated prefix requests.

Result schema version 2 also retains the natural-language query, requested type constraint, and final ranked hits for every query/strategy/cap row. Each hit records its rank, Qdrant point ID, similarity score, type-valid flag, and returned payload. Post-hoc rows contain the accepted type-valid result list; `examined` and `candidates_transferred` describe the broader candidate search needed to produce it.

## Interpretation note

Pre-hoc type validity is expected to be perfect when at least five matching entities exist because the retrieval filter and validity test use the same ontology-type metadata. It measures constraint satisfaction, not independent semantic relevance.

## DBpedia 50-query benchmark

The submitted evaluation uses 50 ATMONTO queries, 50 Brick queries, and 50 DBpedia queries. The submitted DBpedia runs use `benchmarks/dbpedia-us-civic-places-v2.json` through `configs/experiments/dbpedia-minilm-v2.json` and `configs/experiments/dbpedia-bge-v2.json`.

The earlier 42-query DBpedia suite is retained only as a historical development artifact. It is not the DBpedia benchmark reported in the submitted manuscript.

Queries `q043` through `q050` extend coverage of types that were underrepresented in the earlier suite, including Dam, Library, Hospital, EducationalInstitution, Venue, Building, and ArchitecturalStructure. They are phrased as plausible situational searches rather than class definitions while retaining explicit ontology constraints for evaluation.

Recorded 50-query DBpedia results are documented in `results/benchmark-v2/README.md`. The macro-average-by-embedding table combines the 50-query ATMONTO, Brick, and DBpedia summaries using an unweighted arithmetic mean across datasets, so each ontology contributes one third of a reported average row.

If indexing is interrupted after Qdrant has accepted some batches, rerun the same index command with `--resume`. The indexer checks collection dimension, distance, and maximum point count, discovers stable IDs already present, and embeds only missing entity cards. `--resume` and `--replace` are mutually exclusive.

## Filtered-index optimization study

A separate exploratory study evaluated full HNSW coverage and filter-aware payload indexing across all six collections. The resulting Qdrant settings are the final clean-build configuration used for the submitted experiments. See `results/index-optimization/README.md` for configuration details and validation checks. Retrieval calls remain unchanged: no explicit `exact`, `hnsw_ef`, or quantization search parameters are supplied.
