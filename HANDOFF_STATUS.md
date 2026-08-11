# Handoff status

## Current answer

This repository now includes the three exact entity-card JSONL files under `datasets/` through Git LFS. Once committed and pushed to a Git host with LFS enabled, a recipient can reconstruct the vector indexes and rerun all experiments from the repository clone.

## What already works

- exact dataset hashes, sizes, counts, and schemas;
- exact model repositories and revision commits;
- pinned Qdrant image digest and persistent Compose configuration;
- six collection definitions;
- consolidated indexing and evaluation;
- all three paper benchmark suites;
- frozen historical results and generated LaTeX;
- deterministic comparison with the paper baseline;
- validated reproduction of both surviving DBpedia experiment blocks.

## Must be completed before public release

1. Confirm redistribution terms for the three included derived datasets.
2. Commit and push the Git LFS objects to the selected Git host.
3. Select a code license and complete `CITATION.cff`.
4. Run `python scripts/verify_release.py` without migration exceptions.
5. Rehearse the README on a clean machine.

Migrating upstream extractors is strongly recommended for full provenance, but it is not required for the fast reproduction path because the exact entity-card inputs are included.
