import json
from collections import Counter

path = "entities.jsonl"

n = 0
missing = Counter()
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        n += 1
        obj = json.loads(line)

        for k in ["iri", "types", "types_closure", "card_text"]:
            if k not in obj or obj[k] in (None, "", [], {}):
                missing[k] += 1

print("Lines:", n)
print("Missing/empty fields:", dict(missing))