# Final optimized benchmark rerun

Generated 2026-08-14 after clean rebuilding and verifying all six Qdrant collections with the permanent optimized indexing configuration. Each dataset/model run contains 50 queries; DBpedia uses the reviewed `-v2` benchmark extension.

The six raw evaluator outputs are in `results/runs/*-final-optimized.json`. The four CSV files in this directory were generated with:

```powershell
python scripts/generate_optimized_report.py `
  results/runs/atmonto-minilm-final-optimized.json `
  results/runs/atmonto-bge-final-optimized.json `
  results/runs/brick-minilm-final-optimized.json `
  results/runs/brick-bge-final-optimized.json `
  results/runs/dbpedia-minilm-v2-final-optimized.json `
  results/runs/dbpedia-bge-v2-final-optimized.json `
  --output-dir results/final-optimized-rerun
```

The average files use an unweighted macro-average across ATMONTO, Brick, and DBpedia for each method/cap row. Latencies are single local rerun measurements and include the same operations defined by the evaluator; they are not multi-trial hardware-independent estimates.
