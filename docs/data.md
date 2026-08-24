# Data and provenance

The canonical experiment inputs are three enriched, pre-embedding JSONL datasets. Each line is an entity card containing a stable IRI, human-readable embedding text (`card_text`), direct ontology types, transitive type closure, and dataset-specific metadata.

Qdrant collections and vector arrays are derived artifacts rather than source data. They are reconstructed locally from the included entity-card inputs and the pinned embedding-model configurations.

## Exact experiment inputs

The entity-card inputs used by the submitted experiments are included under `datasets/` using Git LFS. Their filenames, record counts, byte sizes, and SHA-256 hashes are recorded in `configs/datasets/`.

| Dataset | Records | Entity-card input |
|---|---:|---|
| ATMONTO | 36,655 | `entities_enriched.jsonl` |
| Brick/Mortar | 19,388 | `brick_entities_enriched.jsonl` |
| DBpedia U.S. civic geography | 23,189 | `dbpedia_us_civic_places_entities_enriched.jsonl` |

File-level manifests for recovered ATMONTO and Brick upstream inputs, plus DBpedia endpoint extraction parameters, are retained in `configs/sources/`. The exact recovered ATMONTO and Brick/Mortar source files are preserved through Git LFS under `provenance/source-inputs/`; redistribution terms must be reviewed before a public release.

## Entity-card contract

All datasets require:

- `iri`: unique entity identifier;
- `card_text`: exact string passed to the embedding model;
- `types`: directly asserted ontology types;
- `types_closure`: direct and inherited types used for filtering and evaluation.

Brick also retains `building` and `bucket`. DBpedia retains `country` and `target_classes`.

## Upstream sources

### ATMONTO

- NASA Air Traffic Management Ontology: https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto
- Richard M. Keller, *The NASA Air Traffic Management Ontology: Technical Documentation*, NASA/TM-2017-219526, 2017.

The paper's retained ATMONTO source consists of 29 Turtle files. Those exact source files and the post-processing entity-card input are preserved with checksums so benchmark reproduction does not depend on mutable upstream hosting.

### Brick and Mortar

- Brick: https://brickschema.org/
- Mortar: https://github.com/gtfierro/mortar
- Mortar graph mirror used for provenance: https://huggingface.co/datasets/gtfierro/mortargraphs
- Bharathan Balaji et al., “Brick: Metadata Schema for Portable Smart Building Applications,” *Applied Energy*, vol. 226, pp. 1273–1292, 2018.
- Gabriel Fierro et al., “Mortar: An Open Testbed for Portable Building Analytics,” *ACM Transactions on Sensor Networks*, vol. 16, no. 1, 2020.

The paper dataset combines the Brick ontology TBox with 45 selected Mortar building/model graphs. The exact recovered source files are preserved under `provenance/source-inputs/brick/`. A currently served Brick Turtle file may differ byte-for-byte from the historical local TBox, so the exact checksummed entity-card input remains the canonical fast-reproduction boundary.

### DBpedia

- DBpedia resources: https://www.dbpedia.org/
- DBpedia licensing: https://www.dbpedia.org/imprint/
- Jens Lehmann et al., “DBpedia: A Large-Scale, Multilingual Knowledge Base Extracted from Wikipedia,” *Semantic Web*, vol. 6, no. 2, pp. 167–195, 2015.

The DBpedia benchmark is a constructed U.S. civic-geography subset retrieved from the public DBpedia SPARQL endpoint. Because a live SPARQL endpoint is mutable, the checksummed pre-embedding entity-card file is the canonical reproduction input for the submitted experiments.

## Licensing and redistribution

The repository's MIT license covers original project software only. It does not relicense upstream ontologies, datasets, or source-derived entity-card artifacts.

Source-specific licensing and attribution details are documented in [`../DATA_LICENSES.md`](../DATA_LICENSES.md). In summary:

- NASA-produced scientific data are generally not copyrighted in the United States unless otherwise marked; NASA should be acknowledged as the source and reuse must not imply endorsement.
- Brick is BSD 3-Clause licensed.
- The upstream Mortar repository is BSD 3-Clause licensed; the Hugging Face `mortargraphs` mirror does not currently state a separate license in its dataset metadata.
- DBpedia releases 3.4 and later are distributed under CC BY-SA 3.0 and the GNU Free Documentation License.

Users redistributing source-derived artifacts should consult the original source terms and retain required attribution/notices.

## Reproduction boundary

The fast reproduction path intentionally begins from the exact entity-card inputs used by the submitted experiments. Rebuilding every entity card from mutable upstream sources is a separate provenance task and is not required to reproduce the benchmark results from the preserved inputs.
