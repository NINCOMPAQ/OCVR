# Ontology Retrieval

Reproducible experiments comparing unconstrained, pre-hoc constrained, and post-hoc constrained vector retrieval over ontology-derived entity cards.

The paper evaluates three datasets—ATMONTO, Brick/Mortar, and a DBpedia US civic-places subset—with two Hugging Face embedding models:

| Dataset | all-MiniLM-L6-v2 | bge-large-en-v1.5 |
|---|---:|---:|
| ATMONTO | 36,655 entities | 36,655 entities |
| Brick/Mortar | 19,388 entities | 19,388 entities |
| DBpedia US civic places | 23,189 entities | 23,189 entities |

The repository stores code, benchmark queries, configuration, checksums, compact results, and the three exact pre-embedding JSONL subsets through Git LFS. It does not store vector embeddings. Users build all six Qdrant collections locally from the included subsets and pinned Hugging Face models.

> **Release status:** the experiment reconstruction path is self-contained once this folder is committed and cloned with Git LFS. The remaining public-release blockers are the repository URL, code license, citation metadata, clean-machine rehearsal, and full upstream extraction migration.

## What is reproducible

Two paths are supported:

- **Fast paper reproduction:** clone the exact entity-card subsets with Git LFS, verify their hashes, embed them, run the experiments, and render the table.
- **Full provenance reproduction:** rebuild those subsets from pinned upstream sources, confirm their hashes, then follow the fast path.

The fast path is the primary way to reproduce the paper. Full extraction provenance is being migrated from the legacy scripts into the `extract` package.

## Requirements

- Python 3.11 or newer
- Docker Desktop or another Docker Compose implementation
- Enough disk space for the three datasets, two embedding models, and six vector collections
- Internet access for the initial dataset/model downloads
- A GPU is optional; CPU indexing is supported but BGE indexing can take considerably longer

Installation and model sources:

- Python: https://www.python.org/downloads/
- Git: https://git-scm.com/downloads
- Git LFS: https://git-lfs.com/
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Qdrant container image: https://hub.docker.com/r/qdrant/qdrant
- MiniLM at the pinned revision: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/c9745ed1d9f207416be6d2e6f8de32d1f16199bf
- BGE at the pinned revision: https://huggingface.co/BAAI/bge-large-en-v1.5/tree/d4aa6901d3a41ba39fb536a557fa166f842b0e09

Commands below use PowerShell. On macOS/Linux, activate the environment with `source .venv/bin/activate` instead.

## Installation

```powershell
git clone git@github.com:NINCOMPAQ/OCVR.git
Set-Location ontology-retrieval
git lfs install
git lfs pull

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

For development and extraction work:

```powershell
python -m pip install -e ".[dev,extract]"
```

## 1. Verify the included subsets

The exact pre-embedding subsets are included under `datasets/` using Git LFS. A normal clone with `git lfs pull` obtains them; no separate dataset host or manual copy is required.

Verify byte-for-byte identity, record counts, required fields, and unique IRIs:

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

See [docs/data.md](docs/data.md) for schemas and provenance status.

Official upstream reference pages are recorded for auditability and future full regeneration. The included JSONL files remain the exact inputs for reproducing the paper:

- NASA ATMONTO: https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto
- Brick downloads and Mortar reference models: https://brickschema.org/resources/
- Mortar graph repository: https://huggingface.co/datasets/gtfierro/mortargraphs
- DBpedia resources: https://www.dbpedia.org/resources/
- DBpedia versioned data catalog: https://databus.dbpedia.org/dbpedia/collections/latest-core

The complete external-link inventory and byte-identity caveats are in [docs/url-audit.md](docs/url-audit.md).

## 2. Start Qdrant

```powershell
docker compose up -d
docker compose ps
```

The Compose file pins the image digest recovered from the paper environment and stores data in a named volume. Qdrant is available at `http://localhost:6333`.

To stop it without deleting data:

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

Index construction performs dataset verification first. It refuses to overwrite an existing collection unless `--replace` is explicitly supplied. Point IDs are deterministic UUIDs derived from dataset ID and entity IRI.

Every clean build uses the final optimized Qdrant configuration:

- HNSW `m=16` and `ef_construct=100`;
- `full_scan_threshold=1000` KB;
- optimizer `indexing_threshold=1000` KB;
- optimizer `default_segment_number=1`;
- no quantization and in-memory HNSW; and
- `types` and `types_closure` keyword indexes created before vector ingestion.

After ingestion, `index` polls Qdrant rather than sleeping for a fixed interval. It returns only when the collection is green, has the exact expected point count and vector configuration, has both required keyword payload indexes, has the intended HNSW/optimizer settings, and has no more than one optimizer-threshold-sized appendable tail left unindexed. Qdrant defines 1 KB of indexing threshold as one 256-dimensional vector, so the permitted tail is `ceil(1000 × 256 / dimension)`: 667 MiniLM vectors or 250 BGE vectors. This follows Qdrant's optimizer semantics while rejecting the wholly unindexed legacy collections. The default readiness timeout is 1,800 seconds; override it when necessary with `--ready-timeout-seconds`.

Verify every collection:

```powershell
Get-ChildItem configs/experiments/*.json | ForEach-Object {
    ontology-retrieval verify-index $_.FullName
}
```

Expected dimensions are 384 for MiniLM and 1,024 for BGE. All collections use cosine distance. `verify-index` applies the same readiness checks and polls until they pass. Evaluation performs a one-shot readiness check before loading the embedding model, so a benchmark cannot silently run against an unready or incompatible collection.

`index --resume` validates vector dimension and distance, HNSW and optimizer settings, required payload indexes, collection status, and maximum point count before reusing a collection. It ingests only missing deterministic IDs and then waits for full readiness. If compatibility checks fail, rebuild explicitly with `--replace`.

The clean MiniLM/BGE integration evidence and exact resulting metadata are recorded in [results/clean-build-validation.md](results/clean-build-validation.md).

### Model revisions

The exact cached Hugging Face revisions used by the original environment are pinned in `configs/models/`:

- MiniLM: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`
- BGE: `d4aa6901d3a41ba39fb536a557fa166f842b0e09`

Direct Python dependencies are pinned in `pyproject.toml`. Package versions recovered from the paper environment, including important transitive ML dependencies, are recorded in `results/paper/provenance.json`.

## 4. Run the experiments

Create one structured result per dataset/model pair:

```powershell
New-Item -ItemType Directory -Force results/runs

ontology-retrieval evaluate configs/experiments/atmonto-minilm.json --output results/runs/atmonto-minilm.json
ontology-retrieval evaluate configs/experiments/atmonto-bge.json --output results/runs/atmonto-bge.json
ontology-retrieval evaluate configs/experiments/brick-minilm.json --output results/runs/brick-minilm.json
ontology-retrieval evaluate configs/experiments/brick-bge.json --output results/runs/brick-bge.json
ontology-retrieval evaluate configs/experiments/dbpedia-minilm.json --output results/runs/dbpedia-minilm.json
ontology-retrieval evaluate configs/experiments/dbpedia-bge.json --output results/runs/dbpedia-bge.json
```

Each file contains per-query results and aggregate summaries. In addition to the paper columns, it records mean similarity, Qdrant request count, and total candidates transferred.

The published DBpedia benchmark has 42 queries. A separate reviewed extension brings it to 50 without changing the paper protocol:

```powershell
ontology-retrieval evaluate configs/experiments/dbpedia-minilm-v2.json --output results/runs/dbpedia-minilm-v2.json
ontology-retrieval evaluate configs/experiments/dbpedia-bge-v2.json --output results/runs/dbpedia-bge-v2.json
```

See [results/benchmark-v2/README.md](results/benchmark-v2/README.md) for the recorded 50-query results and [docs/experiments.md](docs/experiments.md) for the query-design rationale.

Generate the paper's average-by-embedding CSV from the six structured runs (using the two `-v2` DBpedia files for the revised 50-query version):

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

The command rejects missing or duplicate dataset/model pairs and averages each metric equally across the three datasets, matching the paper table's macro-average convention.

See [docs/experiments.md](docs/experiments.md) for exact metric definitions and interpretation cautions.

## Local search webapp

The repository also includes a local FastAPI webapp for interactive OCVR queries. It uses the same dataset, model, and Qdrant collection configs as the experiments. The app does not build, replace, or repair collections; start Qdrant and build the collections you want to query first.

Install the web extra in your virtual environment:

```powershell
python -m pip install -e ".[dev,web]"
```

Start Qdrant and build, or resume, the local vector collections:

```powershell
docker compose up -d

ontology-retrieval index configs/experiments/atmonto-minilm.json --resume
ontology-retrieval index configs/experiments/atmonto-bge.json --resume
ontology-retrieval index configs/experiments/brick-minilm.json --resume
ontology-retrieval index configs/experiments/brick-bge.json --resume
ontology-retrieval index configs/experiments/dbpedia-minilm.json --resume
ontology-retrieval index configs/experiments/dbpedia-bge.json --resume
```

`--resume` is safe for interrupted builds. It validates the existing collection shape, skips deterministic point IDs already present in Qdrant, ingests the missing records, and then waits for the collection to become benchmark-ready. The webapp will report a collection as unavailable until the expected point count and index-readiness checks pass.

Start the local web server:

```powershell
ontology-retrieval serve --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 and run a query such as:

- dataset: `ATMONTO`
- model: `all-MiniLM-L6-v2`
- query: `arrival route segment near Newark`
- constraint: `AirspaceRouteSegment`

The page shows unconstrained, pre-hoc constrained, and post-hoc constrained results side by side. MiniLM is the default model; BGE can be selected from the model dropdown after the dataset selector. The ontology constraint list is populated from each dataset's relevance payload fields and includes every class/type observed in the entity cards.

Each constraint row includes a `?` tooltip. The app scans Turtle ontology files (`*.ttl`) in the project root, the parent workspace directory, and common ontology subdirectories, then uses `rdfs:comment` as the class definition and `rdfs:label` as the display label when a matching class URI is found. If no matching definition is available, the tooltip falls back to the full class URI and matching record count.

Stop the web server with `Ctrl+C` in the terminal where it is running. To stop Qdrant without deleting built collections:

```powershell
docker compose stop
```

## 5. Regenerate the paper table

The historical paper values live in `results/paper/master-results.json`. Render them with:

```powershell
ontology-retrieval render results/paper/master-results.json `
    --csv results/paper/master-results.csv `
    --latex results/paper/master-table.tex
```

The generated LaTeX uses six columns. This corrects the legacy table's seven-column declaration for six-column rows.

Both surviving DBpedia collections have already been exercised through the new evaluator, with exact agreement on all displayed deterministic paper values. See [results/paper/VALIDATION.md](results/paper/VALIDATION.md).

To validate and combine six newly generated runs:

```powershell
ontology-retrieval assemble `
    results/runs/atmonto-minilm.json `
    results/runs/atmonto-bge.json `
    results/runs/brick-minilm.json `
    results/runs/brick-bge.json `
    results/runs/dbpedia-minilm.json `
    results/runs/dbpedia-bge.json `
    --output results/runs/master-results.json
```

The command rejects missing, duplicate, or unexpected dataset/model combinations and requires all 42 aggregate rows. Render the reproduced master file with the same `render` command shown above.

Compare deterministic values with the historical paper baseline (timing is intentionally excluded):

```powershell
ontology-retrieval compare `
    results/runs/master-results.json `
    results/paper/master-results.json
```

## Testing

```powershell
python -m pytest
ruff check .
python scripts/verify_release.py --allow-unpublished-data
```

Unit tests do not download models or full datasets. Full indexing and evaluation are integration workflows because they require Qdrant, model weights, and the research datasets.

## Repository layout

```text
benchmarks/          Paper query suites as data
configs/datasets/   Dataset identity, schema, hashes, and provenance
configs/models/     Hugging Face model and embedding settings
configs/experiments/Six paper-v1 experiment combinations
docs/               Data, protocol, reproduction, and development notes
results/paper/      Frozen historical results and generated table
src/                Consolidated implementation
tests/              Small deterministic unit tests
```

## Reproducibility boundaries

- Semantic/result metrics should reproduce from identical datasets, models, and Qdrant configuration.
- Historical timings are evidence from the original environment, not portable constants.
- Query embedding time is excluded from the paper's retrieval timing.
- Pre-hoc validity uses the same type metadata as its filter, so perfect type-validity is expected when five matching entities exist.
- Qdrant collections and embeddings are derived artifacts and are not required downloads.

## Release blockers

Before making this repository public:

- choose and add the code license;
- confirm redistribution rights for all three entity-card datasets;
- confirm redistribution terms and ensure all three Git LFS objects are pushed;
- migrate and test upstream extraction adapters;
- add authors, paper metadata, and repository URL to `CITATION.cff`;
- validate the historical baseline and newly rebuilt metrics;
- add a clean-machine release rehearsal and CI workflow.

After the paper-v1 release is preserved, a separate benchmark-v2 task will add eight DBpedia queries so all three suites contain 50. Paper-v1 will remain fixed at 42 DBpedia queries for exact comparison with the published table.

The detailed migration sequence is maintained in the parent workspace's `CLEANUP_AND_RELEASE_PLAN.md` while the new project is being assembled.

## Citation and licensing

Citation metadata is provisional in `CITATION.cff`. No code license is asserted yet because that choice belongs to the project owners. Dataset and model licenses remain governed by their respective upstream projects even when derived subsets are redistributed.
