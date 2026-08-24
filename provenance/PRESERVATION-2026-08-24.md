# Lab-PC preservation audit — 2026-08-24

This private-repository preservation pass was performed before retiring the lab PC. It did not rerun experiments or modify canonical datasets, benchmark queries, result files, retrieval code, or Qdrant configuration.

## Already preserved before this pass

- Three exact pre-embedding entity-card datasets under Git LFS, with verified record counts and SHA-256 hashes.
- All 150 final benchmark queries.
- Six schema-v2 final per-query run JSON files containing ranked returned entities, payloads, scores, and validity flags.
- Aggregate tables, the valid@5 figure in PNG/PDF, clean-build validation, dataset characterization, and benchmark environment records.
- Pinned Hugging Face model revisions, Qdrant image digest, collection-building code, and evaluation code.

## Added during this pass

- Exact hash-verified ATMONTO source bundle: 29 Turtle files, 138,993,513 bytes.
- Exact hash-verified Brick source bundle: one TBox plus 45 Mortar models, 5,559,966 bytes.
- Three primary enriched entity-card extraction scripts.
- Forty-six additional top-level legacy Python scripts, including the locally modified historical evaluator.
- Complete `pip freeze --all` output from the project benchmark virtual environment.
- Four compiled paper drafts found in Downloads:

| File | Local timestamp | Bytes | SHA-256 |
|---|---|---:|---|
| `Ontology_Constrained_Vector_Database.pdf` | 2026-03-19 18:22 EDT | 195,862 | `03a9496b6acf68f14b743b86136ede05e6e7b3c9fe007ba9a08acc74ecc34259` |
| `Ontology_Constrained_Vector_Database (1).pdf` | 2026-04-09 18:15 EDT | 199,905 | `e415940b977538cb92886258a859f97646e644043d5a4e34564510e96276cd78` |
| `Ontology_Constrained_Vector_Database (2).pdf` | 2026-08-12 11:20 EDT | 218,371 | `2261921d045b8366040dfdcba1769aefa99c6405ac7e11a62266d9c8df3b59f2` |
| `Ontology_Constrained_Vector_Database (3).pdf` | 2026-08-14 16:48 EDT | 207,484 | `52ad81cba29217cc81647fecf09ec00b8919d11595fe778599d3ee51257f279d` |

## Deliberately not preserved

- Qdrant snapshots: derived from the exact datasets, pinned models, and tracked indexing configuration.
- Hugging Face caches: derived from pinned public model revisions.
- Python bytecode, temporary files, Docker storage, credentials, tokens, and machine-specific caches.
- `results/runs.zip`: a local duplicate archive whose listed JSON members already exist as tracked repository files.
- `Ontology.lnk`: an unrelated Windows shortcut.

## Remaining human action

No local Overleaf source archive, manuscript `.tex`, or bibliography was found. If the live Overleaf project contains newer manuscript material, download its source ZIP and final compiled PDF and preserve them outside or in an appropriate private manuscript repository before losing access. Review source-file redistribution rights before making this repository public.
