# Dataset sources, licensing, and attribution

The MIT license in this repository applies only to software authored for this project. It does **not** relicense upstream ontologies, datasets, or ontology-derived entity-card artifacts.

The benchmark uses four upstream resources: NASA ATMONTO/National Airspace System data, Brick, Mortar building graphs, and DBpedia. Users who redistribute or reuse source-derived data should follow the applicable upstream terms described below.

## NASA ATMONTO and National Airspace System data

**Source**

- NASA Air Traffic Management Ontology (ATMONTO): https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto
- Richard M. Keller, *The NASA Air Traffic Management Ontology: Technical Documentation*, NASA/TM-2017-219526, 2017.

**Use terms**

NASA states that, unless otherwise marked or restricted, NASA-produced scientific data are generally not copyrighted in the United States and may be reproduced and distributed without further permission. NASA also asks users to acknowledge/cite NASA as the source and not imply NASA endorsement.

The ATMONTO-derived entity cards in this repository are therefore **not licensed under this repository's MIT license**. No additional project copyright is asserted over NASA-origin facts or ontology content. Users should consult the NASA source page and any notices attached to the specific source files before redistribution.

## Brick ontology

**Source**

- Brick project: https://brickschema.org/
- Bharathan Balaji et al., “Brick: Metadata Schema for Portable Smart Building Applications,” *Applied Energy*, vol. 226, pp. 1273–1292, 2018. DOI: 10.1016/j.apenergy.2018.02.091.

**Use terms**

Brick is distributed under the BSD 3-Clause License. The Brick Consortium's license permits redistribution and modification provided the copyright notice, conditions, and disclaimer are retained and the names of the copyright holder/contributors are not used to endorse derived products without permission.

Brick-derived ontology content and entity-card fields are not relicensed under MIT by this repository. Reuse should retain the applicable Brick attribution and BSD 3-Clause terms.

## Mortar building models

**Source**

- Mortar repository: https://github.com/gtfierro/mortar
- Mortar graph mirror used for provenance: https://huggingface.co/datasets/gtfierro/mortargraphs
- Gabriel Fierro et al., “Mortar: An Open Testbed for Portable Building Analytics,” *ACM Transactions on Sensor Networks*, vol. 16, no. 1, 2020.

**Use terms**

The upstream `gtfierro/mortar` repository is distributed under the BSD 3-Clause License. The Hugging Face `mortargraphs` mirror currently does not provide a separate license declaration in its dataset metadata. Accordingly, this repository does not attempt to impose a new license on Mortar-derived building graph content.

Users redistributing Mortar-derived data should retain upstream attribution and the BSD 3-Clause notice from the Mortar project and should verify whether any separately obtained graph artifact carries additional terms.

## DBpedia U.S. civic geography subset

**Source**

- DBpedia: https://www.dbpedia.org/
- DBpedia licensing information: https://www.dbpedia.org/imprint/
- Jens Lehmann et al., “DBpedia: A Large-Scale, Multilingual Knowledge Base Extracted from Wikipedia,” *Semantic Web*, vol. 6, no. 2, pp. 167–195, 2015. DOI: 10.3233/SW-140134.

**Use terms**

DBpedia states that releases 3.4 and later are dual-licensed under the Creative Commons Attribution-ShareAlike 3.0 license (CC BY-SA 3.0) and the GNU Free Documentation License (GFDL). DBpedia also requests attribution that keeps DBpedia URIs visible/active when possible.

The DBpedia-derived entity-card subset in this repository is therefore **not covered by the repository's MIT software license**. Redistribution or adaptation of DBpedia-derived data should comply with the applicable DBpedia/Wikipedia licensing and attribution requirements, including share-alike obligations when applicable.

## Repository software

Original software in this repository is released under the MIT License in [`LICENSE`](LICENSE).

Because the repository contains both original software and source-derived data artifacts, the presence of an MIT `LICENSE` file must not be interpreted as changing the licensing status of any upstream ontology, dataset, or derived data file.

## Citation practice

Publications or derivative research using these resources should cite the relevant upstream source(s) above in addition to citing this repository/software. Where source-specific citation guidance is available, follow that guidance as well.
