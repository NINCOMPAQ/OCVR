# Preserved source-level provenance

This directory preserves the exact local source inputs and legacy extraction implementations recovered from the lab machine before it was retired on 2026-08-24.

The canonical inputs for exact paper reproduction remain the three checked-in, checksummed entity-card JSONL files under `datasets/`. The material here supports source-level audit and explains how those cards were originally constructed.

## Contents

- `legacy-extractors/entity_extractor_enriched.py`: ATMONTO entity-card extractor.
- `legacy-extractors/entity_extractor_brick_enriched.py`: Brick/Mortar entity-card extractor.
- `legacy-extractors/entity_extractor_dbpedia_us_civic_places_enriched.py`: DBpedia live-SPARQL entity-card extractor.
- `legacy-code/`: the remaining 46 top-level Python scripts from the original lab workspace, including local-only benchmark, evaluator, indexing, demo, validation, and sampling utilities. This is a forensic snapshot; the maintained implementation remains under `src/`.
- `source-inputs/atmonto/`: the exact 29 ATMONTO Turtle files listed and checksummed in `configs/sources/atmonto.json`.
- `source-inputs/brick/brick_tbox.ttl`: the exact Brick TBox used by the paper pipeline.
- `source-inputs/brick/mortardata-models/`: the exact 45 Mortar building/model Turtle files listed and checksummed in `configs/sources/brick.json`.
- `manuscript-drafts/`: all four compiled OCVR paper PDFs found locally. These are historical drafts, not a declaration of the final submitted manuscript.
- `environment/benchmark-venv-pip-freeze.txt`: complete package freeze from the virtual environment used for the final local benchmark work.
- `final-experiment-artifacts/`: the six final schema-v2 per-query result files and the detailed dataset-characterization audit. These are retained here because the streamlined release tree exposes aggregate benchmark tables but not every ranked hit and validity flag.

All Turtle files are tracked with Git LFS. The source manifests remain authoritative for filenames, byte sizes, SHA-256 hashes, and upstream provenance URLs.

## Important DBpedia boundary

The exact 23,189-record DBpedia experimental subset is preserved as `datasets/dbpedia_us_civic_places_entities_enriched.jsonl`. The original extractor queried a mutable DBpedia SPARQL endpoint, and no complete endpoint response archive or pinned DBpedia dump existed on the lab machine. Consequently, rerunning the legacy extractor against the current endpoint is not expected to recreate identical bytes. Use the frozen entity-card JSONL for exact experiment reproduction; use the preserved extractor only to audit the construction procedure.

## Publication and licensing

These inputs were preserved to prevent loss. Their upstream terms and attributions are documented in `DATA_LICENSES.md` and reproduced where appropriate in `THIRD_PARTY_NOTICES.md`. In particular, the complete source-specific ATMONTO release notice is embedded in three retained ontology files and reproduced in the repository notice; Brick and the upstream Mortar repository use BSD 3-Clause; the Mortar graph mirror declares no separate dataset license; and DBpedia-derived data are treated under CC BY-SA 3.0. The repository's MIT license applies only to original project software.

The lab-PC search found no local Overleaf source ZIP, `.tex` manuscript, or bibliography beyond the generated result table already in the repository. The authors later identified the separately held final PDF submitted to IEEE BigData 2026; it is intentionally not stored in this software/data repository. No acceptance decision has been reported.
