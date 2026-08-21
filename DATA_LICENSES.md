# Dataset sources, licensing, and attribution

The MIT license in this repository applies only to software authored for this project. It does **not** relicense upstream ontologies or datasets.

For the source-derived entity-card artifacts distributed with this repository, we use the following source-compatible treatment:

| Artifact/source | Licensing treatment in this repository |
|---|---|
| Original project software | MIT |
| NASA ATMONTO/NAS-derived content | No additional project license asserted; follow NASA source terms and attribution guidance |
| Brick/Mortar-derived entity cards | BSD 3-Clause terms and upstream notices retained |
| DBpedia-derived entity cards | CC BY-SA 3.0 selected from DBpedia's dual-license terms |

Full third-party notices are reproduced in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## NASA ATMONTO and National Airspace System data

**Source**

- NASA Air Traffic Management Ontology (ATMONTO): https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto
- Richard M. Keller, *The NASA Air Traffic Management Ontology: Technical Documentation*, NASA/TM-2017-219526, 2017.

**Use terms**

NASA states that, unless otherwise marked or restricted, NASA-produced scientific data are generally not copyrighted in the United States and may be reproduced and distributed without further permission. NASA also asks users to acknowledge/cite NASA as the source and not imply NASA endorsement.

Accordingly, this project does not place its MIT software license over NASA-origin ontology/data content and does not assert an additional project copyright over NASA-origin facts. Users should consult the source page and any notices attached to the specific NASA source files before redistribution.

## Brick ontology

**Source**

- Brick project: https://brickschema.org/
- Brick repository: https://github.com/BrickSchema/Brick
- Bharathan Balaji et al., “Brick: Metadata Schema for Portable Smart Building Applications,” *Applied Energy*, vol. 226, pp. 1273–1292, 2018. DOI: 10.1016/j.apenergy.2018.02.091.

**Use terms**

Brick is distributed under the BSD 3-Clause License. Redistribution and modification are permitted provided the upstream copyright notice, conditions, and disclaimer are retained and the names of the copyright holder/contributors are not used for endorsement without permission.

Brick-derived ontology content in the combined Brick/Mortar entity-card artifact is therefore distributed with the applicable BSD 3-Clause notice retained in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), rather than being relicensed under MIT.

## Mortar building models

**Source**

- Mortar repository: https://github.com/gtfierro/mortar
- Mortar graph mirror used for provenance: https://huggingface.co/datasets/gtfierro/mortargraphs
- Gabriel Fierro et al., “Mortar: An Open Testbed for Portable Building Analytics,” *ACM Transactions on Sensor Networks*, vol. 16, no. 1, 2020.

**Use terms**

The upstream `gtfierro/mortar` repository is distributed under the BSD 3-Clause License. The Hugging Face `mortargraphs` mirror currently does not provide a separate license declaration in its dataset metadata.

For the combined Brick/Mortar entity-card artifact, this project retains the Mortar BSD 3-Clause notice and attribution rather than asserting a new MIT license over Mortar-origin graph content. Users who obtain graph artifacts from another host should verify whether that copy carries additional terms.

## DBpedia U.S. civic geography subset

**Source**

- DBpedia: https://www.dbpedia.org/
- DBpedia licensing information: https://www.dbpedia.org/imprint/
- Jens Lehmann et al., “DBpedia: A Large-Scale, Multilingual Knowledge Base Extracted from Wikipedia,” *Semantic Web*, vol. 6, no. 2, pp. 167–195, 2015. DOI: 10.3233/SW-140134.

**Use terms**

DBpedia states that releases 3.4 and later are dual-licensed under the Creative Commons Attribution-ShareAlike 3.0 license (CC BY-SA 3.0) and the GNU Free Documentation License (GFDL). DBpedia also requests attribution that keeps DBpedia URIs visible/active when possible.

For redistribution of the DBpedia-derived U.S. civic-geography entity-card subset in this repository, we select **CC BY-SA 3.0** from DBpedia's dual-license options to the extent that the subset constitutes an adaptation of DBpedia content. The entity cards retain source IRIs to support attribution. The repository's MIT software license does not apply to this data artifact.

## Repository software

Original software in this repository is released under the MIT License in [`LICENSE`](LICENSE).

Because the repository contains both original software and source-derived data artifacts, the presence of an MIT `LICENSE` file must not be interpreted as changing the licensing status of any upstream ontology, dataset, or derived data file.

## Citation practice

Publications or derivative research using these resources should cite the relevant upstream source(s) above in addition to citing this repository/software. Where source-specific citation guidance is available, follow that guidance as well.
