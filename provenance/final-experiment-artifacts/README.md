# Final experiment artifacts

This directory preserves detailed paper artifacts that are intentionally outside the streamlined public-facing result tree.

## Per-query results

`per-query-results/` contains the six final optimized benchmark executions: one for each combination of the three datasets and two embedding models. Each JSON file records all 50 queries, every retrieval mode and cap, aggregate metrics, and the actual ranked returned entities with payloads, scores, and ontology-validity flags.

The canonical benchmark definitions remain in `benchmarks/`, and the release-facing aggregate CSV tables and figures remain in `results/benchmark/`.

## Dataset characterization

`dataset_characterization.json` and `dataset_characterization.md` preserve the detailed counts used when characterizing the three paper datasets. The JSON version is machine-readable; the Markdown version includes the recommended paper table and provenance notes.

These files are historical records of the final lab-machine state. They should not be silently regenerated or edited to match a later run.

`checksums.sha256` records the SHA-256 digest of every preserved result and characterization artifact in this directory. The release verifier checks these hashes, validates the six run schemas and query coverage, and confirms that their summaries reproduce the checked-in aggregate CSV values.
