# Data and provenance

The canonical experiment inputs are three enriched, pre-embedding JSONL datasets. Each line is an entity card containing a stable IRI, human-readable embedding text (`card_text`), direct types, transitive type closure, and ontology-specific metadata.

The repository intentionally does not treat Qdrant collections or vector arrays as source data. Those are reconstructed locally using the model and experiment configurations.

## Current artifacts

The exact entity-card subsets are included under `datasets/` with Git LFS. Their filenames, record counts, byte sizes, and SHA-256 hashes are in `configs/datasets/`. File-level manifests for the recovered ATMONTO and Brick upstream inputs, plus the DBpedia endpoint extraction parameters, are in `configs/sources/`.

Official upstream references:

- NASA ATMONTO: https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto
- Brick schema and Mortar model downloads: https://brickschema.org/resources/
- Mortar graphs: https://huggingface.co/datasets/gtfierro/mortargraphs
- DBpedia resources: https://www.dbpedia.org/resources/
- DBpedia latest-core documentation: https://www.dbpedia.org/resources/latest-core/
- DBpedia Databus collection: https://databus.dbpedia.org/dbpedia/collections/latest-core

These links document provenance but do not currently reproduce every upstream byte used by the paper. Sampled Mortar model downloads match the local files exactly; the currently served Brick 1.4.4 Turtle file does not match the local paper TBox hash. The NASA landing page does not currently expose the local 29-file input bundle through a verified immutable download. This does not block experiment reproduction because the exact post-preprocessing, pre-embedding entity cards are included and checksummed.

## Entity-card contract

All datasets require:

- `iri`: unique entity identifier;
- `card_text`: exact string passed to the embedding model;
- `types`: directly asserted types;
- `types_closure`: direct and inherited types used for filtering and evaluation.

Brick also retains `building` and `bucket`. DBpedia retains `country` and `target_classes`.

## Full provenance still to migrate

The legacy root contains the current ATMONTO, Brick, and DBpedia extraction implementations. They will be migrated into ontology-specific adapters after the included entity-card artifacts and paper baseline have been frozen. DBpedia requires special care because a live SPARQL endpoint is mutable; the release must preserve the exact pre-enrichment boundary data or reference a pinned dump.

Redistribution licenses and upstream version identifiers must be reviewed before artifact publication.
