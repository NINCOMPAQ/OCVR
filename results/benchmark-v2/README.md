# DBpedia 50-query benchmark v2

These results extend the immutable 42-query paper-v1 DBpedia suite with eight reviewed natural-language queries (`q043`–`q050`). They are a new protocol, not corrected paper-v1 values.

Evaluated 2026-08-12 against the two reconstructed 23,189-point Qdrant collections. Deterministic metric values are shown to four decimals. Timing is local wall-clock time for Qdrant requests and is not expected to reproduce exactly on other machines.

| Model | Strategy | Limit | valid@5 | success@5 | time (s) | examined |
|---|---|---:|---:|---:|---:|---:|
| all-MiniLM-L6-v2 | Unconstrained | 5 | 0.6880 | 0.4800 | 0.0082 | 5.00 |
| all-MiniLM-L6-v2 | Pre-hoc | 5 | 1.0000 | 1.0000 | 0.0188 | 5.00 |
| all-MiniLM-L6-v2 | Post-hoc | 25 | 0.8960 | 0.8800 | 0.0107 | 25.00 |
| all-MiniLM-L6-v2 | Post-hoc | 100 | 0.9480 | 0.9000 | 0.0183 | 34.00 |
| all-MiniLM-L6-v2 | Post-hoc | 200 | 0.9720 | 0.9400 | 0.0238 | 41.50 |
| all-MiniLM-L6-v2 | Post-hoc | 400 | 0.9800 | 0.9800 | 0.0282 | 47.00 |
| all-MiniLM-L6-v2 | Post-hoc | 2000 | 0.9800 | 0.9800 | 0.0669 | 79.00 |
| bge-large-en-v1.5 | Unconstrained | 5 | 0.6680 | 0.4000 | 0.0069 | 5.00 |
| bge-large-en-v1.5 | Pre-hoc | 5 | 1.0000 | 1.0000 | 0.0221 | 5.00 |
| bge-large-en-v1.5 | Post-hoc | 25 | 0.9160 | 0.8800 | 0.0140 | 25.00 |
| bge-large-en-v1.5 | Post-hoc | 100 | 0.9600 | 0.9600 | 0.0203 | 31.50 |
| bge-large-en-v1.5 | Post-hoc | 200 | 0.9800 | 0.9800 | 0.0204 | 35.50 |
| bge-large-en-v1.5 | Post-hoc | 400 | 0.9800 | 0.9800 | 0.0248 | 39.50 |
| bge-large-en-v1.5 | Post-hoc | 2000 | 0.9920 | 0.9800 | 0.0601 | 71.50 |

Reproduce the structured per-query outputs from the repository root:

```powershell
New-Item -ItemType Directory -Force results/runs
ontology-retrieval evaluate configs/experiments/dbpedia-minilm-v2.json --output results/runs/dbpedia-minilm-v2.json
ontology-retrieval evaluate configs/experiments/dbpedia-bge-v2.json --output results/runs/dbpedia-bge-v2.json
```

The raw run files are generated artifacts and are intentionally ignored by Git. Each contains all 350 per-query/strategy rows plus the aggregate summary.

## Average across all three ontologies

`average-by-embedding-v2.csv` is the revised form of the paper's average-by-embedding table. It was generated from fresh local ATMONTO and Brick runs (50 queries each) and the DBpedia-v2 runs (50 queries) using the command documented in the repository README. Every row is the unweighted mean of the three ontology summaries.

All six Qdrant collections were verified green before evaluation. Point counts were 36,655 for ATMONTO, 19,388 for Brick, and 23,189 for DBpedia under both embedding models; dimensions were 384 for MiniLM and 1,024 for BGE, with cosine distance throughout. Model revisions are pinned in `configs/models/`.

The CSV's valid@5, success@5, and score values are the revised experimental results. Its times were measured locally on 2026-08-12 and should not be treated as hardware-independent performance claims.
