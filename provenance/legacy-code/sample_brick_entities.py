from __future__ import annotations

from pathlib import Path
import json
import random


MIN_PATH = Path("brick_entities.jsonl")
ENRICHED_PATH = Path("brick_entities_enriched.jsonl")
SAMPLE_SIZE = 5
SEED = 7


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"Missing file: {path.resolve()}")
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def print_samples(title: str, records: list[dict]) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    for i, rec in enumerate(records, 1):
        print(f"\nSample {i}")
        print(f"Label: {rec.get('label')}")
        print(f"Building: {rec.get('building')}")
        if "bucket" in rec:
            print(f"Bucket: {rec.get('bucket')}")
        print(f"IRI: {rec.get('iri')}")
        print(f"Card: {rec.get('card_text')}")


def main() -> None:
    rng = random.Random(SEED)
    min_records = load_records(MIN_PATH)
    enriched_records = load_records(ENRICHED_PATH)

    min_sample = rng.sample(min_records, min(SAMPLE_SIZE, len(min_records)))
    enriched_sample = rng.sample(enriched_records, min(SAMPLE_SIZE, len(enriched_records)))

    print_samples("BRICK MINIMAL CARD SAMPLES", min_sample)
    print_samples("BRICK ENRICHED CARD SAMPLES", enriched_sample)


if __name__ == "__main__":
    main()
