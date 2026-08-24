import json
from collections import Counter

path = "entities.jsonl"
targets = [
    "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
    "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
    "https://data.nasa.gov/ontologies/atmonto/NAS#InternationalAirport",
]

counts = Counter()
total = 0

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        total += 1
        # Count by first matching target type in direct types
        for t in targets:
            if t in obj["types"]:
                counts[t] += 1
                break

print("Total:", total)
for t in targets:
    print(counts[t], t)