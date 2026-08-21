# Ontology-Constrained Vector Retrieval

Code and reproducibility materials for **Ontology-Constrained Vector Retrieval**.

This repository compares three retrieval strategies over ontology-backed entity collections:

- **Unconstrained vector retrieval**: semantic similarity only.
- **Pre-hoc ontology-constrained retrieval**: ontology-derived type constraints are supplied to Qdrant during retrieval.
- **Post-hoc ontology filtering**: unrestricted candidates are retrieved first and filtered afterward using the same type-validity criterion.

## Paper benchmark

The submitted paper evaluates 150 natural-language query--constraint pairs across three datasets and two embedding models.

| Dataset | Indexed entities | Queries |
|---|---:|---:|
| ATMONTO | 36,655 | 50 |
| Brick/Mortar | 19,388 | 50 |
| DBpedia U.S. civic geography | 23,189 | 50 |
| **Total** | **79,232** | **150** |

Embedding models:

- `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- `BAAI/bge-large-en-v1.5` (1,024 dimensions)

The repository contains benchmark queries, experiment configuration, model revisions, checksums, evaluation code, compact result artifacts, the exact pre-embedding entity-card inputs used by the experiments, and an interactive local web interface. Vector embeddings and Qdrant collections are reconstructed locally rather than stored in the repository.

## Interactive query interface

The repository includes a local FastAPI interface for exploring the same unconstrained, pre-hoc, and post-hoc retrieval strategies used in the paper. The interface shows the three result sets side by side and marks whether each returned entity satisfies the selected ontology constraint.

After installing the project and building the Qdrant collections you want to query, install the web extra and start the server:

```powershell
python -m pip install -e ".[web]"
ontology-retrieval serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

Example query:

- dataset: `ATMONTO`
- model: `all-MiniLM-L6-v2`
- query: `arrival route segment near Newark`
- constraint: `AirspaceRouteSegment`

The web app uses the same dataset, model, and Qdrant collection configuration as the benchmark experiments. It does not create or repair collections automatically; start Qdrant and build the desired collections first.

## Reproducibility overview

The primary reproduction path starts from the exact checksummed entity-card inputs included under `datasets/` using Git LFS:

1. clone the repository and pull the Git LFS objects;
2. verify the included entity-card inputs;
3. start Qdrant;
4. build the six dataset--embedding collections;
5. run the 150-query benchmark; and
6. regenerate the reported result tables/figures as needed.

The semantic/result metrics should reproduce when the same entity-card inputs, pinned model revisions, and Qdrant configuration are used. Wall-clock latency is environment dependent; the paper reports the timings observed on the stated experimental workstation.

## Requirements

- Python 3.11 or newer
- Git and Git LFS
- Docker Desktop or another Docker Compose implementation
- enough disk space for three datasets, two embedding models, and six vector collections
- internet access for the initial model downloads
- GPU optional; CPU indexing is supported, although BGE indexing can take considerably longer

Commands below use PowerShell. On macOS/Linux, activate the environment with `source .venv/bin/activate` instead.

## Installation

```powershell
git clone https://github.com/NINCOMPAQ/OCVR.git
Set-Location OCVR
git lfs install
git lfs pull

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

For development, extraction utilities, plots, and the web interface:

```powershell
python -m pip install -e ".[dev,extract,plot,web]"
```

## 1. Verify the included entity-card inputs

```powershell
ontology-retrieval data verify configs/datasets/atmonto.json
ontology-retrieval data verify configs/datasets/brick.json
ontology-retrieval data verify configs/datasets/dbpedia-us-civic-places.json
```

Expected inputs:

| File | Records | SHA-256 |
|---|---:|---|
| `entities_enriched.jsonl` | 36,655 | `22880d1a37838869d693e6b97b9932ff53dd23e89ea4f1f688d2827227a6ad7d` |
| `brick_entities_enriched.jsonl` | 19,388 | `ebe4d0579ceb5e6d5828ee335e7f516bbc5967ff8be42aecec2744af0bed0007` |
| `dbpedia_us_civic_places_entities_enriched.jsonl` | 23,189 | `1c9fc4b32266b9d45c46db2f7425d3b0288845d3368834751fdc30589b688c53` |

See [`docs/data.md`](docs/data.md) for schemas and provenance details and [`DATA_LICENSES.md`](DATA_LICENSES.md) for source attribution and licensing notes.

## 2. Start Qdrant

```powershell
docker compose up -d
docker compose ps
```

Qdrant is available locally at `http://localhost:6333`.

To stop it without deleting the constructed collections:

```powershell
docker compose stop
```

Do not use `docker compose down --volumes` unless you intentionally want to delete all locally constructed collections.

## 3. Build the six collections

```powershell
ontology-retrieval index configs/experiments/atmonto-minilm.json
ontology-retrieval index configs/experiments/atmonto-bge.json
ontology-retrieval index configs/experiments/brick-minilm.json
ontology-retrieval index configs/experiments/brick-bge.json
ontology-retrieval index configs/experiments/dbpedia-minilm.json
ontology-retrieval index configs/experiments/dbpedia-bge.json
```

Every clean build uses the paper configuration:

- HNSW `m=16` and `ef_construct=100`;
- `full_scan_threshold=1000` KB;
- optimizer `indexing_threshold=1000` KB;
- optimizer `default_segment_number=1`;
- no vector quantization and in-memory HNSW; and
- `types` and `types_closure` keyword indexes created before vector ingestion.

Expected dimensions are 384 for MiniLM and 1,024 for BGE. All collections use cosine distance.

The exact model revisions are pinned in `configs/models/`:

- MiniLM: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`
- BGE: `d4aa6901d3a41ba39fb536a557fa166f842b0e09`

Direct Python dependencies are pinned in `pyproject.toml`; additional package provenance from the paper environment is recorded in `results/paper/provenance.json`.

## 4. Run the submitted 150-query benchmark

Create one structured result per dataset/model pair:

```powershell
New-Item -ItemType Directory -Force results/runs

ontology-retrieval evaluate configs/experiments/atmonto-minilm.json --output results/runs/atmonto-minilm.json
ontology-retrieval evaluate configs/experiments/atmonto-bge.json --output results/runs/atmonto-bge.json
ontology-retrieval evaluate configs/experiments/brick-minilm.json --output results/runs/brick-minilm.json
ontology-retrieval evaluate configs/experiments/brick-bge.json --output results/runs/brick-bge.json
ontology-retrieval evaluate configs/experiments/dbpedia-minilm-v2.json --output results/runs/dbpedia-minilm-v2.json
ontology-retrieval evaluate configs/experiments/dbpedia-bge-v2.json --output results/runs/dbpedia-bge-v2.json
```

The submitted paper uses the 50-query DBpedia benchmark in the two `*-v2` experiment configurations above. The earlier 42-query DBpedia suite and corresponding artifacts are retained only as historical development records and are not the benchmark reported in the submitted manuscript.

Generate the macro-average-by-embedding CSV used for the submitted 150-query evaluation:

```powershell
ontology-retrieval average `
    results/runs/atmonto-minilm.json `
    results/runs/atmonto-bge.json `
    results/runs/brick-minilm.json `
    results/runs/brick-bge.json `
    results/runs/dbpedia-minilm-v2.json `
    results/runs/dbpedia-bge-v2.json `
    --output results/runs/average-by-embedding-v2.csv
```

See [`results/benchmark-v2/README.md`](results/benchmark-v2/README.md) for the recorded 50-query DBpedia results and [`docs/experiments.md`](docs/experiments.md) for protocol and metric details.

## 5. Interactive web app

To query already-built collections interactively:

```powershell
python -m pip install -e ".[web]"
ontology-retrieval serve --host 127.0.0.1 --port 8000
```

The interface supports ATMONTO, Brick, and DBpedia collections under both evaluated embedding models. It exposes ontology classes available in each dataset and displays unconstrained, pre-hoc, and post-hoc results side by side.

## 6. Testing

```powershell
python -m pytest
ruff check .
```

Unit tests do not download full models or datasets. Full indexing and evaluation are integration workflows because they require Qdrant, model weights, and the research datasets.

## Repository layout

```text
benchmarks/           Benchmark query suites
configs/datasets/     Dataset identity, schema, hashes, and provenance
configs/models/       Pinned embedding-model settings
configs/experiments/  Experiment configurations
 datasets/            Exact pre-embedding entity-card inputs (Git LFS)
docs/                 Data, protocol, reproduction, and development notes
results/               Recorded benchmark and validation artifacts
src/                   Implementation, retrieval logic, and web app
tests/                 Deterministic unit tests
```

## Dataset sources and citations

The benchmark uses the following upstream resources. Full licensing and attribution notes are in [`DATA_LICENSES.md`](DATA_LICENSES.md).

- **ATMONTO:** Richard M. Keller, *The NASA Air Traffic Management Ontology: Technical Documentation*, NASA/TM-2017-219526, 2017. Source: NASA Air Traffic Management Ontology and associated National Airspace System data.
- **Brick:** Bharathan Balaji et al., “Brick: Metadata Schema for Portable Smart Building Applications,” *Applied Energy*, vol. 226, pp. 1273--1292, 2018, doi:10.1016/j.apenergy.2018.02.091.
- **Mortar:** Gabriel Fierro et al., “Mortar: An Open Testbed for Portable Building Analytics,” *ACM Transactions on Sensor Networks*, vol. 16, no. 1, 2020.
- **DBpedia:** Jens Lehmann et al., “DBpedia: A Large-Scale, Multilingual Knowledge Base Extracted from Wikipedia,” *Semantic Web*, vol. 6, no. 2, pp. 167--195, 2015, doi:10.3233/SW-140134.

Official source pages:

- NASA ATMONTO: https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto
- Brick: https://brickschema.org/
- Mortar: https://github.com/gtfierro/mortar
- Mortar graph mirror used for provenance: https://huggingface.co/datasets/gtfierro/mortargraphs
- DBpedia: https://www.dbpedia.org/

## Reproducibility boundaries

- Semantic/result metrics should reproduce from identical entity-card inputs, model revisions, and Qdrant configuration.
- Historical timings are evidence from the original environment, not portable constants.
- Query embedding time is excluded from the paper's retrieval timing.
- Pre-hoc validity uses the same ontology-type metadata as its filter, so perfect type validity is expected when five matching entities exist.
- Qdrant collections and embeddings are derived artifacts and are not required downloads.

## License

The software written for this repository is released under the [MIT License](LICENSE).

Upstream ontologies, datasets, and ontology-derived entity-card artifacts are **not relicensed under MIT**. They remain subject to their applicable upstream terms and attribution requirements. See [`DATA_LICENSES.md`](DATA_LICENSES.md) before redistributing dataset artifacts.

## Citation

Citation metadata for this software is provided in [`CITATION.cff`](CITATION.cff). Please also cite the relevant upstream datasets/ontologies listed above when using their data.
