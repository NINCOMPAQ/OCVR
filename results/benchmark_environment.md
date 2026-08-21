# Benchmark execution environment

Captured on 2026-08-14 from the lab machine used for the 150-query benchmark. This record was collected without rerunning any experiment.

## Hardware and operating system

| Component | Benchmark environment |
|---|---|
| Operating system | Microsoft Windows 11 Enterprise, version 10.0.26200, build 26200, 64-bit |
| CPU | Intel(R) Core(TM) Ultra 9 285K |
| CPU cores | 24 physical cores, 24 logical processors |
| System RAM | 33,775,415,296 bytes (31.46 GiB; nominally 32 GB) |
| Discrete GPU | NVIDIA RTX 4000 Ada Generation, 20,475 MiB, driver 571.59 |
| Integrated GPU | Intel(R) Graphics, driver 32.0.101.6881 |
| PyTorch CUDA availability | `False` (`torch.cuda.device_count() == 0`); the project Python environment did not expose the NVIDIA GPU to PyTorch |

## Software

| Component | Version |
|---|---|
| Python | 3.13.5 |
| Docker client | 29.2.1 |
| Docker server/engine | 29.2.1 |
| Qdrant | 1.17.0, commit `4ab6d2ee0f6c718667e553b1055f3e944fef025f` |
| `qdrant-client` | 1.17.0 |
| `sentence-transformers` | 5.4.0 |
| PyTorch (`torch`) | 2.11.0 |
| `transformers` | 5.5.3 |

Qdrant ran in Docker on the same physical lab machine as the Python evaluation client. The container used Docker bridge networking and published container port 6333 to host port 6333. The evaluator used `http://localhost:6333`.

The reported retrieval latency wraps each `QdrantClient.query_points(...)` call with `time.perf_counter()` (`src/ontology_retrieval/evaluate.py::_query`). It therefore includes Python client serialization/deserialization, localhost HTTP request/response overhead, and Qdrant query processing. Post-hoc latency is the sum of those timed Qdrant calls. Query embedding occurs before the timer and is excluded; local post-hoc validity filtering and loop overhead occur outside the per-request timers and are also excluded.

## Experiment implementation

The experiment implementation and configuration used for the recorded benchmark were present at commit:

`ad9e7cccb279d96b1ed8be3c74f006942efcf530`

The environment record itself does not alter experiment code, datasets, queries, retrieval configuration, or result values.

## Collection service evidence

- Qdrant root endpoint `http://localhost:6333/` reported version 1.17.0 and the commit above.
- The running container published `6333/tcp` and `6334/tcp` on the host and reported status `running` when this record was collected.
- `compose.yaml` pins the Qdrant image digest: `qdrant/qdrant@sha256:f1c7272cdac52b38c1a0e89313922d940ba50afd90d593a1605dbbc214e66ffb`.
