# Reproduction guide

The README is the authoritative command sequence. This document records the two supported levels of reproduction.

## Fast paper reproduction

1. Clone the exact entity-card datasets included through Git LFS.
2. Verify their checksums and schemas.
3. Start the pinned Qdrant service.
4. build and verify all six collections;
5. run all six experiment configurations;
6. assemble the master results and render CSV/LaTeX.

The model configurations pin the exact Hugging Face snapshot commits recovered from the original paper environment.

## Full provenance reproduction

The full path begins with pinned upstream ontology/data releases and regenerates each entity-card JSONL before following the fast path. Extraction adapters are not yet migrated from the legacy root, so this is a documented release work item rather than a completed workflow.

## Timing

Exact historical timings are retained as paper evidence. New timing comparisons should record CPU/GPU, operating system, Qdrant image digest, Python lockfile, warm-up behavior, strategy ordering, repetition count, and uncertainty.
