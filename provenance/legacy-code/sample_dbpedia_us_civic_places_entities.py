import json
from pathlib import Path


PATH = Path("dbpedia_us_civic_places_entities_enriched.jsonl")


def main() -> None:
    if not PATH.exists():
        raise SystemExit(f"Missing file: {PATH.resolve()}")

    with PATH.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            rec = json.loads(line)
            print("=" * 100)
            print("iri:", rec.get("iri"))
            print("label:", rec.get("label"))
            print("target_classes:", rec.get("target_classes"))
            print("types:", rec.get("types"))
            print("types_closure sample:", rec.get("types_closure", [])[:12])
            print("card_text:", rec.get("card_text"))
            if i >= 5:
                break


if __name__ == "__main__":
    main()
