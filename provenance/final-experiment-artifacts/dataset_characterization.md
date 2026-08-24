# Dataset and benchmark characterization for the IEEE BigData paper

Computed from the final repository datasets and benchmarks plus the live final Qdrant state on 2026-08-14. No experiment inputs, queries, retrieval code, or collection settings were changed.

## A. Recommended paper table

| Dataset | Domain | RDF triples | Indexed entities | Indexed classes | Target classes | Queries |
|---|---|---:|---:|---:|---:|---:|
| ATMONTO | Air traffic management | 2,931,368 | 36,655 | 22 | 6 | 50 |
| Brick | Building systems and HVAC | 121,209 | 19,388 | 130 | 35 | 50 |
| DBpedia US Civic Geography | US civic places and institutions | not recoverable* | 23,189 | 75 | 14 | 50 |

**Recommended definitions.** “Indexed classes” is the number of distinct class IRIs appearing in `types_closure` among indexed entity records. This is the most defensible operational count because `types_closure` is stored in Qdrant and is the primary field used for ontology-constrained retrieval; it includes direct types and represented ancestors. “Target classes” is the number of distinct class IRIs in the union of `constraint_any` across the final 50-query benchmark. For completeness, those classes form 5 ATMONTO, 31 Brick, and 16 DBpedia order-insensitive constraint families.

\* DBpedia was extracted through a mutable SPARQL endpoint. The retained artifact is an entity-card subset, not an RDF dump or complete response archive, so its exact source triple count cannot be reconstructed. Counting JSON fields as triples would be incorrect.

The three benchmarks contain **150 queries total**. The three datasets contain **79,232 indexed entities total**, with a separate MiniLM and BGE vector for every entity.

## B. Detailed audit

### ATMONTO

- **RDF scope:** the extractor unioned 29 Turtle files listed in `configs/sources/atmonto.json`. The per-file graphs contain 2,931,864 triples in total; after RDF graph de-duplication, the graph actually used by the pipeline contains **2,931,368 unique triples**. The indexed dataset is a curated subset selected from that graph using eight configured target types and a cap of 8,000 per target, not every subject in the RDF graph.
- **Indexed entities:** **36,655** processed records. Both `atmonto_minilm_enriched` and `atmonto_bge_large_en_v1_5_enriched` contain exactly 36,655 points and were green when checked.
- **Ontology classes:** **2,466** distinct subjects explicitly declared as either `owl:Class` or `rdfs:Class` in the 29-file graph; **7** distinct directly asserted types occur among indexed entities; **22** distinct classes occur in indexed `types_closure` values.
- **Type cardinality per entity:** direct types min/median/max = **1/1/2**; closure classes min/median/max = **3/7/10**.
- **Operational type families:** six of the extractor’s eight configured target types are represented: AirspaceRouteSegment 8,000; InternationalAirport 5,145; IntersectionFix 8,000; LatLonFix 8,000; METARreport 2,488; TAFmeteorologicalCondition 5,022. PhysicalRunway and OperationalRunway have zero indexed records. These counts sum to 36,655 because the extractor assigns each output to the first matching configured target for cap accounting.
- **Benchmark:** exactly **50 queries**, targeting **6 distinct class IRIs** arranged into **5 constraint families**:

  | Constraint family (`atm:`/`nas:`/`data:` abbreviated) | Queries |
  |---|---:|
  | `atm:AirspaceRouteSegment` | 12 |
  | `atm:IntersectionFix OR atm:LatLonFix` | 12 |
  | `nas:Airport` | 6 |
  | `data:METARreport` | 10 |
  | `data:TAFmeteorologicalCondition` | 10 |

Namespaces: `atm:` = `https://data.nasa.gov/ontologies/atmonto/ATM#`; `nas:` = `https://data.nasa.gov/ontologies/atmonto/NAS#`; `data:` = `https://data.nasa.gov/ontologies/atmonto/data#`.

### Brick

- **RDF scope:** the extractor unioned the retained `brick_tbox.ttl` and **45** selected Mortar building/model Turtle files: **46 files total**. Their separate graphs contain 123,123 triples; the de-duplicated graph actually loaded contains **121,209 unique triples**. The TBox alone contains **53,960 triples**. This is the selected Mortar corpus used by the experiment, not all Brick deployments or every upstream Mortar graph.
- **Indexed entities:** **19,388** processed records. Both `brick_mortardata_minilm_enriched` and `brick_mortardata_bge_large_en_v1_5_enriched` contain exactly 19,388 points and were green when checked.
- **Ontology classes:** **1,786** distinct subjects explicitly declared as either `owl:Class` or `rdfs:Class` in the retained TBox; **85** distinct directly asserted types occur among indexed entities; **130** distinct classes occur in indexed `types_closure` values. The direct count faithfully includes every type in the final data, including an `owl:Ontology`-typed record; it was not cleaned retrospectively.
- **Type cardinality per entity:** direct types min/median/max = **1/1/2**; closure classes min/median/max = **1/7/10**.
- **Operational type families:** the extractor’s semantic buckets represented in the indexed data are point 11,797; location 4,275; equipment 3,151; and other 165. No record is assigned the system bucket. These are extractor buckets, not ontology class counts.
- **Benchmark:** exactly **50 queries**, targeting **35 distinct class IRIs** arranged into **31 order-insensitive constraint families**:

  | Constraint family (`brick:` abbreviated) | Queries |
  |---|---:|
  | `Air_Flow_Setpoint OR Supply_Air_Flow_Setpoint` | 2 |
  | `Air_Handler_Unit` | 3 |
  | `Chilled_Water_Return_Temperature_Sensor` | 1 |
  | `Chilled_Water_Supply_Temperature_Sensor` | 1 |
  | `Chiller` | 1 |
  | `Cooling_Command OR Valve_Command` | 2 |
  | `Damper` | 1 |
  | `Damper_Position_Command OR Damper_Position_Setpoint` | 1 |
  | `Discharge_Air_Temperature_Sensor` | 2 |
  | `Floor` | 1 |
  | `HVAC_Zone` | 3 |
  | `Heating_Command` | 1 |
  | `Heating_Command OR Mode` | 1 |
  | `Mixed_Air_Temperature_Sensor` | 1 |
  | `Occupancy_Sensor` | 1 |
  | `Occupied_Cooling_Temperature_Setpoint` | 1 |
  | `Occupied_Heating_Temperature_Setpoint` | 1 |
  | `Outside_Air_Temperature_Sensor` | 1 |
  | `RVAV OR VAV` | 2 |
  | `Reheat_Coil` | 2 |
  | `Return_Air_Temperature_Sensor` | 1 |
  | `Room` | 2 |
  | `Start_Stop_Command` | 1 |
  | `Supply_Air_Flow_Sensor` | 2 |
  | `Supply_Air_Static_Pressure_Sensor` | 1 |
  | `Supply_Air_Temperature_Sensor` | 2 |
  | `Supply_Air_Temperature_Setpoint` | 3 |
  | `Unoccupied_Air_Temperature_Cooling_Setpoint` | 1 |
  | `Unoccupied_Air_Temperature_Heating_Setpoint` | 1 |
  | `Zone_Air_Temperature_Sensor` | 4 |
  | `Zone_Air_Temperature_Setpoint` | 3 |

Namespace: `brick:` = `https://brickschema.org/schema/Brick#`. Two benchmark rows express `Cooling_Command OR Valve_Command` in opposite list orders; they are one semantic constraint family and are counted together here.

### DBpedia US Civic Geography

- **RDF scope:** an exact source triple count is **not determinable**. The extractor queried `https://dbpedia.org/sparql` on 2026-04-30 and retained entity cards, not a pinned RDF dump, triple-level subset, or complete SPARQL response archive. The DBpedia ontology class graph used to construct closure was also not frozen, so a total schema-class count cannot be recovered exactly.
- **What the subset includes:** deduplicated DBpedia resources with directly asserted `dbo:country dbr:United_States` and at least one of 15 configured extraction targets: EducationalInstitution, University, School, City, Town, Village, ArchitecturalStructure, Building, ReligiousBuilding, Infrastructure, Dam, Venue, Stadium, Library, or Hospital. Enrichment fetched DBpedia ontology direct types and superclass closure, English labels/abstracts, selected location relations, and selected facts. It is neither all DBpedia nor all US DBpedia resources.
- **Indexed entities:** **23,189** processed records. Both `dbpedia_us_civic_places_minilm_enriched` and `dbpedia_us_civic_places_bge_large_en_v1_5_enriched` contain exactly 23,189 points and were green when checked.
- **Ontology classes:** total classes defined in the source DBpedia schema = **not recoverable from retained state**; **69** distinct directly asserted types occur among indexed entities; **75** distinct classes occur in indexed `types_closure` values.
- **Type cardinality per entity:** direct types min/median/max = **2/5/12**; closure classes min/median/max = **2/6/13**.
- **Operational type families:** 12 configured extraction targets appear in retained `target_classes`: Building 2,071; City 2,713; Dam 809; Hospital 94; Library 180; ReligiousBuilding 530; School 4,111; Stadium 133; Town 4,974; University 939; Venue 554; Village 7,529. Counts overlap because an entity can match several targets. EducationalInstitution, ArchitecturalStructure, and Infrastructure have zero direct `target_classes` entries, although the first two are valid superclass constraints represented through closure.
- **Benchmark:** the final experiments explicitly override the historical 42-query dataset default with `benchmarks/dbpedia-us-civic-places-v2.json`. That final file has exactly **50 queries**, targeting **14 distinct class IRIs** arranged into **16 constraint families**:

  | Constraint family (`dbo:` abbreviated) | Queries |
  |---|---:|
  | `ArchitecturalStructure OR Building` | 2 |
  | `Building` | 4 |
  | `City` | 4 |
  | `Dam` | 4 |
  | `EducationalInstitution` | 2 |
  | `Hospital` | 4 |
  | `Library` | 4 |
  | `ReligiousBuilding` | 4 |
  | `School` | 4 |
  | `Stadium` | 2 |
  | `Stadium OR Venue` | 1 |
  | `Town` | 3 |
  | `Town OR Village` | 1 |
  | `University` | 4 |
  | `Venue` | 3 |
  | `Village` | 4 |

Namespace: `dbo:` = `http://dbpedia.org/ontology/`.

## C. Provenance

| Reported quantity | Direct evidence and computation |
|---|---|
| Processed records, bytes, hashes | `PYTHONPATH=src python -m ontology_retrieval.cli data verify configs/datasets/<dataset>.json`; this verified the tracked JSONL files against their config metadata. Files: `datasets/entities_enriched.jsonl`, `datasets/brick_entities_enriched.jsonl`, and `datasets/dbpedia_us_civic_places_entities_enriched.jsonl`. |
| RDF source scope and file hashes | `configs/sources/atmonto.json`, `configs/sources/brick.json`, and `configs/sources/dbpedia-us-civic-places.json`. |
| ATMONTO RDF triples/classes | Read-only `rdflib.Graph` parse and union of the 29 local manifest files, matching `entity_extractor_enriched.py::load_all_ttl`; `len(graph)` for triples and the union of subjects typed `owl:Class`/`rdfs:Class` for classes. |
| Brick RDF triples/classes | Read-only `rdflib.Graph` parse of `brick_tbox.ttl` plus all 45 local `brick_mortardata_models/*.ttl`, matching `entity_extractor_brick_enriched.py::load_graphs`; class total is the `owl:Class`/`rdfs:Class` union in the TBox. |
| DBpedia extraction boundary | `configs/sources/dbpedia-us-civic-places.json` and `entity_extractor_dbpedia_us_civic_places_enriched.py`; the absence of a pinned dump/response archive is why triple and total schema-class counts are not reported. |
| Direct and closure class counts; min/median/max | Streaming JSON parsing of the actual tracked entity-card files; set union of `types` and `types_closure`, plus list-length statistics over every record. |
| Operational family counts | ATMONTO: configured extractor targets intersected with each record’s `types`; Brick: exact `bucket` field counts; DBpedia: exact `target_classes` field counts. |
| Benchmark totals and target frequencies | Direct parse of `benchmarks/atmonto.json`, `benchmarks/brick.json`, and `benchmarks/dbpedia-us-civic-places-v2.json`; `constraint_any` lists were canonicalized as order-insensitive sets before frequency counting. |
| Final DBpedia benchmark selection | `configs/experiments/dbpedia-minilm-v2.json` and `configs/experiments/dbpedia-bge-v2.json`, which override the dataset config’s historical 42-query benchmark path. |
| Qdrant point counts | Live `GET /collections/<collection>` against Qdrant 1.17.0 on 2026-08-14 for all six experiment collections. Every collection reported green and the point counts stated above. |

### Exactness limitations

1. The exact ATMONTO and Brick RDF numbers were computed from source files whose byte sizes and SHA-256 hashes are preserved in the tracked manifests. The exact bundles are now tracked through Git LFS under `provenance/source-inputs/atmonto/` and `provenance/source-inputs/brick/`, so the counts can be recomputed after `git lfs pull`.
2. DBpedia’s exact triple count and full schema-class count cannot be established from the retained state. The processed 23,189-record entity-card artifact is exact and tracked, but it is not an RDF triple snapshot.
3. “Ontology type family” is not a common formal field across all three extractors. The optional family statistics above are explicitly operational and should not be placed in a cross-dataset table without that qualification.
4. `types_closure` class counts include represented external/root classes where present (for example OWL/RDFS, REC, Schema.org, or GoodRelations ancestors). This is intentional for the recommended operational “Indexed classes” definition.

## D. Machine-readable companion

The complete structured counts, full target IRIs, source URLs, collection names, provenance, and limitations are stored in `results/dataset_characterization.json`.
