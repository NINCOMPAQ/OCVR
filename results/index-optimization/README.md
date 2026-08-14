# Qdrant filtered-index optimization experiment

This exploratory run tested whether correcting Qdrant index coverage would accelerate pre-hoc ontology-constrained search. It is separate from the paper-v1 and DBpedia-v2 protocols and does not replace their results.

## Change under test

Qdrant 1.17.0 initially had eight segments per collection. Four of six collections reported zero HNSW-indexed vectors, and both DBpedia collections lacked keyword payload indexes. Before changing state, collection-level snapshots were created for all six collections.

The experiment then:

1. created `types` and `types_closure` keyword indexes where absent;
2. set `optimizers_config.default_segment_number` to 1;
3. set `optimizers_config.indexing_threshold` to 1,000 KB;
4. set `hnsw_config.full_scan_threshold` to 1,000 KB; and
5. waited until every collection was green, had two segments, and reported all vectors indexed.

No vectors, payload values, query texts, embedding models, or evaluation code changed.

## Result

Pre-hoc search became faster in all six dataset/model combinations. MiniLM's macro-average fell from 14.267 ms to 9.784 ms (1.46x faster; 31.4% reduction). BGE's fell from 17.917 ms to 11.586 ms (1.55x faster; 35.3% reduction). Type validity remained exactly 1.0000 for every combination.

The optimization also changed approximate nearest-neighbor rankings. Five pre-hoc score changes were negligible, but ATMONTO MiniLM's mean score fell by 0.008186. At the default `hnsw_ef=100`, its optimized top five overlapped exact constrained top five by only 85.6%. Raising `hnsw_ef` to 256 improved overlap to 92.4% but made that query path slower than its original baseline.

Unconstrained and post-hoc metrics also changed because they began using HNSW rather than the original full scans. Large-cap post-hoc searches sometimes became slower. Therefore this configuration is not adopted as the repository default.

See `pre-hoc-before-after.csv` for the six primary comparisons and `ef-sweep.csv` for constrained ANN overlap against exact filtered top-five results. Timings are single-run local wall-clock measurements and should be confirmed with repeated warm runs before publication.

## State restoration

After collecting results, all six collection snapshots were recovered and the original configuration was explicitly restored:

- `default_segment_number=0`;
- `indexing_threshold=10000` KB;
- `full_scan_threshold=10000` KB;
- eight original segments per collection;
- original HNSW coverage; and
- original payload schemas, including no DBpedia payload indexes.

All six restored collections were verified green with their expected point counts. The live Qdrant state therefore continues to support the existing reproduction workflow.

## Complete optimized results

The `optimized-results/` directory reports the revised valid@5, success@5, score, and timing values from the optimized runs. It contains one dataset-level and one cross-dataset-average CSV for each embedding model.

Regenerate those four files from the six ignored structured run artifacts:

```powershell
python scripts/generate_optimized_report.py `
    results/runs/atmonto-minilm-optimized.json `
    results/runs/atmonto-bge-optimized.json `
    results/runs/brick-minilm-optimized.json `
    results/runs/brick-bge-optimized.json `
    results/runs/dbpedia-minilm-v2-optimized.json `
    results/runs/dbpedia-bge-v2-optimized.json `
    --output-dir results/index-optimization/optimized-results
```

The generator requires exactly one 50-query run for every dataset/model pair and rejects incomplete input matrices.
