import json

path = "entities.jsonl"
bad = 0
checked = 0

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        t = set(obj["types"])
        tc = set(obj["types_closure"])
        if not t.issubset(tc):
            bad += 1
        checked += 1

print("Checked:", checked)
print("Violations (types not subset of types_closure):", bad)