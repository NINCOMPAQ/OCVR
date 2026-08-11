# Paper-v1 validation status

Validation date: 2026-08-11

The consolidated evaluator was run against both surviving DBpedia Qdrant collections using the pinned model revisions and the 42-query natural-language paper suite.

| Collection | Points | Dimension | Deterministic comparison |
|---|---:|---:|---|
| `dbpedia_us_civic_places_minilm_enriched` | 23,189 | 384 | PASS |
| `dbpedia_us_civic_places_bge_large_en_v1_5_enriched` | 23,189 | 1,024 | PASS |

For both models, every aggregate `valid@5`, `success@5`, and `examined` value matched the historical paper table at its displayed precision across unconstrained, pre-hoc, and all five post-hoc caps.

Latency was deliberately excluded from the equality requirement because it changes with cache state, hardware, and runtime conditions. The validation runs were stored under the ignored `results/runs/` directory rather than committed as new paper measurements.

ATMONTO and Brick validation remains pending reconstruction of their four missing Qdrant collections.
