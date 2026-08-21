# Reproduction guide

The README is the authoritative command sequence. This document summarizes the two reproduction levels supported by the repository.

## Fast benchmark reproduction

1. Clone the exact entity-card datasets included through Git LFS.
2. Verify their checksums and schemas.
3. Start the pinned Qdrant service.
4. Build and verify all six collections.
5. Run the six submitted experiment configurations.
6. Generate the aggregate result artifacts.

The model configurations pin the exact Hugging Face snapshot commits recovered from the experimental environment. The submitted benchmark uses 50 queries each for ATMONTO, Brick, and DBpedia; the DBpedia runs use the `*-v2` experiment configurations documented in the README.

## Upstream provenance reproduction

The repository also records upstream ontology/data sources and source manifests for provenance. Because several upstream resources are mutable or no longer reproduce the historical source bytes exactly, the checksummed pre-embedding entity-card files are the canonical boundary for reproducing the submitted benchmark. See `docs/data.md` and `DATA_LICENSES.md` for details.

## Timing

Exact historical timings are retained as evidence from the reported environment and are not expected to reproduce identically on other machines. New timing comparisons should record the relevant hardware, operating system, Qdrant version, software environment, warm-up behavior, and repetition protocol.
