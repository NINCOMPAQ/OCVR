import json, random

path = "entities_enriched.jsonl"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in random.sample(lines, 8):
    obj = json.loads(line)
    print("\n---")
    print("IRI:", obj["iri"])
    print("Label:", obj.get("label"))
    print("Types:", obj["types"][:3])
    print("Card:", obj["card_text"][:500])