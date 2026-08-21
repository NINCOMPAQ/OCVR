# External URL audit

Audit date: 2026-08-21

Every external dependency named in the README has an explicit URL. Exact experiment inputs use checksums in addition to URLs.

| Item | URL | Role/status |
|---|---|---|
| Python | https://www.python.org/downloads/ | Runtime installer |
| Git | https://git-scm.com/downloads | Source-control client |
| Git LFS | https://git-lfs.com/ | Downloads the included JSONL subset objects during clone |
| Docker Desktop | https://www.docker.com/products/docker-desktop/ | Container runtime |
| Qdrant image | https://hub.docker.com/r/qdrant/qdrant | Image registry; Compose pins a digest |
| MiniLM | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/c9745ed1d9f207416be6d2e6f8de32d1f16199bf | Exact model revision |
| BGE | https://huggingface.co/BAAI/bge-large-en-v1.5/tree/d4aa6901d3a41ba39fb536a557fa166f842b0e09 | Exact model revision |
| NASA ATMONTO | https://data.nasa.gov/dataset/the-nasa-air-traffic-management-ontology-atmonto | Official provenance landing page; not a verified immutable source bundle |
| Brick resources | https://brickschema.org/resources/ | Official schema and Mortar model downloads |
| Brick 1.4.4 Turtle | https://brickschema.org/schema/1.4.4/Brick.ttl | Official version URL; current bytes may differ from the historical paper TBox |
| Mortar models | https://brickschema.org/ttl/mortar/ | Direct-file base URL; sampled files match retained local hashes |
| Mortar graphs | https://huggingface.co/datasets/gtfierro/mortargraphs | Public graph mirror used for provenance |
| DBpedia endpoint | https://dbpedia.org/sparql | Endpoint used for extraction; mutable |
| DBpedia resources | https://www.dbpedia.org/resources/ | Official data-access overview |
| DBpedia Databus | https://databus.dbpedia.org/dbpedia/collections/latest-core | Versioned data catalog |

## Repository URL

GitHub repository page: https://github.com/NINCOMPAQ/OCVR

The three JSONL experiment inputs are tracked with Git LFS inside the repository and therefore do not require separate artifact URLs.

## URL policy

- Use direct HTTPS artifact URLs in machine-readable configuration where practical.
- Pin immutable versions or commits wherever the host supports them.
- Verify downloaded bytes before use.
- Keep human-facing landing pages for citation/provenance, but do not substitute them for immutable artifacts when exact byte identity matters.
- When upstream bytes differ from the retained experiment input, use the included checksummed entity-card artifact as the reproduction boundary and document the upstream relationship.
