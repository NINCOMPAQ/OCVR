import json, random

path = "entities.jsonl"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in random.sample(lines, 5):
    obj = json.loads(line)
    print("\n---")
    print("IRI:", obj["iri"])
    print("Label:", obj.get("label"))
    print("Types:", obj["types"][:3])
    print("Closure size:", len(obj["types_closure"]))
    print("Card:", obj["card_text"][:200])