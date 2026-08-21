# Benchmark results

These artifacts reproduce the 150-query benchmark configuration and deterministic retrieval metrics reported in the paper. Each dataset/model combination contains 50 queries, and all six Qdrant collections were clean-built and verified under the same indexing configuration before evaluation.

The four CSV files summarize Valid@5, AllValid@5 (`success_at_5`), mean similarity, and retrieval time by dataset and embedding model. Validity and similarity values correspond to the reported benchmark. The timing columns are measurements from the clean-build rerun preserved in this repository and may differ from the manuscript's single-run latency measurements because wall-clock retrieval time is environment- and run-dependent. The post-hoc figure is provided in both PNG and vector PDF formats.

Structured per-query outputs can be regenerated from the repository root:

```powershell
New-Item -ItemType Directory -Force results/runs

ontology-retrieval evaluate configs/experiments/atmonto-minilm.json --output results/runs/atmonto-minilm.json
ontology-retrieval evaluate configs/experiments/atmonto-bge.json --output results/runs/atmonto-bge.json
ontology-retrieval evaluate configs/experiments/brick-minilm.json --output results/runs/brick-minilm.json
ontology-retrieval evaluate configs/experiments/brick-bge.json --output results/runs/brick-bge.json
ontology-retrieval evaluate configs/experiments/dbpedia-minilm.json --output results/runs/dbpedia-minilm.json
ontology-retrieval evaluate configs/experiments/dbpedia-bge.json --output results/runs/dbpedia-bge.json
```

Regenerate the summary CSVs with:

```powershell
python scripts/generate_optimized_report.py `
  results/runs/atmonto-minilm.json `
  results/runs/atmonto-bge.json `
  results/runs/brick-minilm.json `
  results/runs/brick-bge.json `
  results/runs/dbpedia-minilm.json `
  results/runs/dbpedia-bge.json `
  --output-dir results/benchmark
```

Regenerate the post-hoc figure with:

```powershell
python -m pip install -e ".[plot]"
python scripts/plot_valid_at_5.py `
  --minilm results/benchmark/minilm-by-dataset.csv `
  --bge results/benchmark/bge-by-dataset.csv `
  --output results/benchmark/valid-at-5-by-candidate-limit.png `
  --pdf results/benchmark/valid-at-5-by-candidate-limit.pdf
```

The average CSVs use an unweighted macro-average across ATMONTO, Brick, and DBpedia for each method/cap row. Retrieval times are local wall-clock measurements and are not expected to reproduce exactly on different hardware or across repeated runs.
