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

## DBpedia benchmark v2

The paper-v1 suites contain 50 ATMONTO queries, 50 Brick queries, and 42 DBpedia queries. The 42-query DBpedia suite remains unchanged because its denominator is encoded in the published results.

`benchmarks/dbpedia-us-civic-places-v2.json` extends DBpedia to 50 queries under a separate protocol. Queries `q043` through `q050` cover types that were underrepresented in the original tail: Dam, Library, Hospital, EducationalInstitution, Venue, Building, and ArchitecturalStructure. They are phrased as plausible situational searches rather than class definitions. Some deliberately admit neighboring interpretations—for example, an evening-class query can evoke a school, college, or other educational institution—while retaining a defensible ontology constraint.

Run the extension with `configs/experiments/dbpedia-minilm-v2.json` and `configs/experiments/dbpedia-bge-v2.json`. Results from a successful local run against the reconstructed collections are recorded in `results/benchmark-v2/README.md`.

The revised average-by-embedding table uses the unchanged 50-query ATMONTO and Brick runs plus the 50-query DBpedia-v2 runs. `ontology-retrieval average` computes an unweighted arithmetic mean across those three dataset summaries for every model, strategy, and retrieval cap. Thus each ontology contributes one third of a row regardless of its query count.

If indexing is interrupted after Qdrant has accepted some batches, rerun the same index command with `--resume`. The indexer checks collection dimension, distance, and maximum point count, discovers stable IDs already present, and embeds only missing entity cards. `--resume` and `--replace` are mutually exclusive.

## Filtered-index optimization study

A separate exploratory study forced full HNSW coverage and filter-aware payload indexing across all six collections. It improved pre-hoc latency but changed approximate rankings and did not consistently improve post-hoc search. The paper configuration remains unchanged. See `results/index-optimization/README.md` for configuration, results, accuracy checks, and restoration details.
