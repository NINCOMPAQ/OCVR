# Qdrant filtered-index optimization experiment

This exploratory study tested whether improved HNSW coverage and filter-aware payload indexing would accelerate pre-hoc ontology-constrained search. The resulting settings were adopted as the repository's benchmark indexing configuration.

## Change under test

Qdrant 1.17.0 initially had eight segments per collection. Four of six collections reported zero HNSW-indexed vectors, and both DBpedia collections lacked keyword payload indexes. Collection-level snapshots were created before the exploratory changes.

The study then:

1. created `types` and `types_closure` keyword indexes where absent;
2. set `optimizers_config.default_segment_number` to 1;
3. set `optimizers_config.indexing_threshold` to 1,000 KB;
4. set `hnsw_config.full_scan_threshold` to 1,000 KB; and
5. waited until every collection was green and appropriately indexed.

No vectors, payload values, query texts, embedding models, or evaluation code changed.

## Result

Pre-hoc search became faster in all six dataset/model combinations. MiniLM's macro-average fell from 14.267 ms to 9.784 ms (1.46x faster; 31.4% reduction). BGE's fell from 17.917 ms to 11.586 ms (1.55x faster; 35.3% reduction). Type validity remained exactly 1.0000 for every combination.

The optimization also changed approximate nearest-neighbor rankings. Five pre-hoc score changes were negligible, but ATMONTO MiniLM's mean score fell by 0.008186. At the default `hnsw_ef=100`, its optimized top five overlapped exact constrained top five by 85.6%. Raising `hnsw_ef` to 256 improved overlap to 92.4% but made that query path slower than its original baseline.

Unconstrained and post-hoc metrics also changed because they began using HNSW rather than full scans. Large-cap post-hoc searches sometimes became slower. The benchmark therefore reruns every retrieval strategy against the same indexed state rather than mixing results from different index configurations.

See `pre-hoc-before-after.csv` for the six primary comparisons and `ef-sweep.csv` for constrained ANN overlap against exact filtered top-five results.

The `optimized-results/` directory contains the intermediate summary tables collected during this indexing study. The paper's benchmark artifacts are in `results/benchmark/`.
