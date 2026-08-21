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

## Upstream provenance

The repository also records upstream ontology/data sources and source manifests for provenance. Because several upstream resources are mutable or no longer reproduce the original source bytes exactly, the checksummed pre-embedding entity-card files are the canonical boundary for reproducing the benchmark. See `docs/data.md` and `DATA_LICENSES.md` for details.

## Timing

Recorded timings are evidence from the reported environment and are not expected to reproduce identically on other machines. New timing comparisons should record the relevant hardware, operating system, Qdrant version, software environment, warm-up behavior, and repetition protocol.
