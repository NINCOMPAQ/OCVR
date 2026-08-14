# Optimized clean-build validation

Validated 2026-08-14 with Qdrant 1.17.0. All six paper collections were deleted and rebuilt from the tracked entity-card datasets using the normal `ontology-retrieval index ... --replace` command. No restored collection state was reused.

| Collection | Model | Status | Points | Indexed vectors | Indexed fraction | Segments | Dimension | Distance |
|---|---|---|---:|---:|---:|---:|---:|---|
| `atmonto_minilm_enriched` | all-MiniLM-L6-v2 | green | 36,655 | 36,096 | 0.984750 | 2 | 384 | cosine |
| `atmonto_bge_large_en_v1_5_enriched` | bge-large-en-v1.5 | green | 36,655 | 36,608 | 0.998718 | 2 | 1,024 | cosine |
| `brick_mortardata_minilm_enriched` | all-MiniLM-L6-v2 | green | 19,388 | 19,200 | 0.990303 | 2 | 384 | cosine |
| `brick_mortardata_bge_large_en_v1_5_enriched` | bge-large-en-v1.5 | green | 19,388 | 19,200 | 0.990303 | 2 | 1,024 | cosine |
| `dbpedia_us_civic_places_minilm_enriched` | all-MiniLM-L6-v2 | green | 23,189 | 23,040 | 0.993575 | 2 | 384 | cosine |
| `dbpedia_us_civic_places_bge_large_en_v1_5_enriched` | bge-large-en-v1.5 | green | 23,189 | 23,040 | 0.993575 | 2 | 1,024 | cosine |

All six collections reported:

- HNSW `m=16`, `ef_construct=100`, `full_scan_threshold=1000` KB, and `on_disk=false`;
- optimizer `default_segment_number=1` and `indexing_threshold=1000` KB; and
- `types` and `types_closure` payload indexes with Qdrant `keyword` schema.

Each difference between `points_count` and `indexed_vectors_count` is a small appendable tail below the optimizer threshold. Qdrant defines 1 KB of indexing threshold as one 256-dimensional vector. The readiness rule therefore permits at most `ceil(1000 * 256 / dimension)` unindexed vectors: 667 for MiniLM or 250 for BGE. Every collection's tail is below the applicable bound and passed `verify-index`.

Three representative DBpedia queries were exercised for each model through unchanged unrestricted, `types_closure MatchAny` constrained, and cap-25 local post-hoc paths. Every request completed. Constrained retrieval returned five type-valid results for all six query/model cases. Post-hoc returned zero valid results for q001 at cap 25, preserving the expected failure behavior rather than padding or substituting results.

Finally, `index --resume` was run against the completed DBpedia MiniLM collection. It validated the existing vector/index configuration and payload schemas, found all deterministic point IDs already present, performed no replacement, and passed the same readiness gate.
