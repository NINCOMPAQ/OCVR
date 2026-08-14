# Final optimized benchmark rerun

Generated 2026-08-14 after clean rebuilding and verifying all six Qdrant collections with the permanent optimized indexing configuration. Each dataset/model run contains 50 queries; DBpedia uses the reviewed `-v2` benchmark extension.

The six raw evaluator outputs are in `results/runs/*-final-optimized.json`. They use result schema version 2 and retain the query text, constraint, and final ranked hits for every method and post-hoc cap. Each hit includes its rank, Qdrant point ID, score, validity flag, and full returned payload. The four CSV files in this directory were generated with:

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

Regenerate the post-hoc `valid@5` figure in PNG and vector PDF formats with:

```powershell
python -m pip install -e ".[plot]"

python scripts/plot_valid_at_5.py `
  --minilm results/final-optimized-rerun/minilm-by-dataset.csv `
  --bge results/final-optimized-rerun/bge-by-dataset.csv `
  --output results/final-optimized-rerun/valid-at-5-by-candidate-limit.png `
  --pdf results/final-optimized-rerun/valid-at-5-by-candidate-limit.pdf
```
