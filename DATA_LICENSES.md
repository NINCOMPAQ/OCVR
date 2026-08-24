# Dataset sources, licensing, and attribution

The MIT license in this repository applies only to software authored for this project. It does **not** relicense upstream ontologies or datasets.

For the source-derived entity-card artifacts distributed with this repository, we use the following source-compatible treatment:

| Artifact/source | Licensing treatment in this repository |
|---|---|
| Original project software | MIT |
| NASA ATMONTO/NAS-derived content | ATMONTO's embedded release terms; no additional project license asserted |
| OpenFlights-origin content incorporated by ATMONTO | Open Database License 1.0 and Database Contents License; source attribution retained |
| Brick ontology content | BSD 3-Clause terms and notice retained |
| Mortar-model content | Mortar attribution and upstream BSD notice retained; no additional project license asserted |
| DBpedia-derived entity cards | CC BY-SA 3.0 selected from DBpedia's dual-license terms |

Full third-party notices are reproduced in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## NASA ATMONTO and National Airspace System data

**Source**

- NASA Air Traffic Management Ontology (ATMONTO): https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto
- Richard M. Keller, *The NASA Air Traffic Management Ontology: Technical Documentation*, NASA/TM-2017-219526, 2017.

**Controlling source notice**

ATMONTO provides its own `dcterms:license` release notice inside `atmontoCore.ttl`, `atmonto.ttl`, and `atmontoPlus.ttl`. That source-specific notice is more relevant than a generic statement about NASA material. It:

- credits NASA's Aviation Operations and Safety Program;
- identifies incorporated material from the FAA, U.S. Department of Transportation, NOAA, CAST/ICAO, and OpenFlights;
- says that the incorporated material remains subject to applicable distribution terms and conditions;
- provides the data as-is, without warranty, and notes that NASA did not validate the third-party data;
- warns that export of technical data may require U.S. authorization; and
- says that the data, including modified or enhanced versions, must not be offered for sale.

The complete notice is retained in the source files and reproduced in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), with only the source-list formatting normalized. This repository acknowledges Richard M. Keller and NASA as the ATMONTO source, retains the component-source acknowledgments, does not imply NASA endorsement, does not apply MIT to the ATMONTO data, and does not offer the data for sale.

The NASA Open Data Portal marks ATMONTO's access level as public. NASA's general guidance also says NASA material should be acknowledged and should not be used to imply endorsement, while warning that marked third-party material can carry separate rights. Those general principles do not replace ATMONTO's embedded notice.

## OpenFlights content incorporated by ATMONTO

ATMONTO's embedded notice says that airport and airline data from OpenFlights are distributed according to OpenFlights' license and disclaimer. OpenFlights states that its Airport, Airline, Plane, and Route databases are available under the [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/) and that rights in individual contents are licensed under the [Database Contents License](https://opendatacommons.org/licenses/dbcl/1-0/).

To the extent that an ATMONTO source file or derived entity-card database contains OpenFlights-origin database material, that material remains subject to those terms, including source acknowledgment and applicable share-alike obligations. The repository retains source IRIs and identifies both ATMONTO/NASA and OpenFlights in its notices. Nothing in the MIT software license overrides the OpenFlights terms.

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

The upstream `gtfierro/mortar` repository is distributed under the BSD 3-Clause License. The Brick resources page identifies the graph files as anonymized representations of real buildings originally published in the Mortar paper. The Hugging Face `mortargraphs` mirror currently provides the 45 graph files but does not declare a separate dataset license in its metadata.

This repository therefore retains the Mortar BSD notice and full scholarly/source attribution but does not assert that MIT applies to Mortar-origin graph content. This accurately records what the upstream sources state without inventing a separate license for the graph mirror.

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
