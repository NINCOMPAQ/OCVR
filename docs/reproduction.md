# Reproduction guide

The README is the authoritative command sequence. This document summarizes the two reproduction levels supported by the repository.

## Benchmark reproduction

1. Clone the entity-card datasets included through Git LFS.
2. Verify their checksums and schemas.
3. Start the pinned Qdrant service.
4. Build and verify all six collections.
5. Run the six experiment configurations under `configs/experiments/`.
6. Generate the aggregate result artifacts under `results/benchmark/`.

The model configurations pin the exact Hugging Face snapshot commits recovered from the experimental environment. The benchmark uses 50 queries each for ATMONTO, Brick, and DBpedia.

For audit without rerunning Qdrant, the six final schema-v2 per-query outputs are preserved under `provenance/final-experiment-artifacts/per-query-results/`. `scripts/verify_release.py` checks their hashes, schema and query coverage, and confirms that their summaries reproduce the checked-in aggregate CSV values.

## Upstream provenance

The repository records upstream ontology/data sources and source manifests for provenance. Exact recovered ATMONTO and Brick/Mortar source files are preserved under `provenance/source-inputs/`; the DBpedia live-endpoint response was not available. Because several upstream resources are mutable, the checksummed pre-embedding entity-card files remain the canonical boundary for reproducing the benchmark. See `docs/data.md`, `provenance/README.md`, and `DATA_LICENSES.md` for details.

## Timing

Recorded timings are evidence from the reported environment and are not expected to reproduce identically on other machines. New timing comparisons should record the relevant hardware, operating system, Qdrant version, software environment, warm-up behavior, and repetition protocol.
