from pathlib import Path
from collections import Counter
from rdflib import Graph

TTL_DIR = Path("allFilesTTL")

KEYWORDS = [
    "lat", "lon", "long", "latitude", "longitude",
    "location", "point", "coord", "position", "x", "y"
]

g = Graph()
for fp in sorted(TTL_DIR.glob("*.ttl")):
    g.parse(fp, format="turtle")

print("Total triples:", len(g))

pred_counts = Counter()

for _, p, _ in g:
    p_str = str(p).lower()
    if any(k in p_str for k in KEYWORDS):
        pred_counts[str(p)] += 1

print("\nCoordinate/location-related predicates:")
for pred, count in pred_counts.most_common(100):
    print(f"{count:10d}  {pred}")