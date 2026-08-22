from __future__ import annotations

import hashlib
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .config import DatasetConfig


@dataclass(frozen=True)
class VerificationResult:
    path: Path
    records: int
    bytes: int
    sha256: str


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def iter_entity_cards(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc


def verify_dataset(path: Path, config: DatasetConfig) -> VerificationResult:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")
    size = path.stat().st_size
    digest = sha256_file(path)
    count = 0
    seen_iris: set[str] = set()
    required = {config.text_field, "iri", *config.payload_fields}
    for count, record in enumerate(iter_entity_cards(path), start=1):
        missing = required - record.keys()
        if missing:
            raise ValueError(f"Record {count} is missing fields: {sorted(missing)}")
        iri = record["iri"]
        if iri in seen_iris:
            raise ValueError(f"Duplicate IRI at record {count}: {iri}")
        seen_iris.add(iri)
    errors = []
    if size != config.bytes:
        errors.append(f"bytes: expected {config.bytes}, found {size}")
    if count != config.records:
        errors.append(f"records: expected {config.records}, found {count}")
    if digest != config.sha256:
        errors.append(f"sha256: expected {config.sha256}, found {digest}")
    if errors:
        raise ValueError("Dataset verification failed: " + "; ".join(errors))
    return VerificationResult(path=path, records=count, bytes=size, sha256=digest)


def download_dataset(config: DatasetConfig, destination: Path) -> Path:
    if not config.artifact_url:
        raise ValueError(
            f"No artifact URL is published for {config.id}. "
            "Place the file manually and run `data verify`."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    urllib.request.urlretrieve(config.artifact_url, partial)
    verify_dataset(partial, config)
    partial.replace(destination)
    return destination
