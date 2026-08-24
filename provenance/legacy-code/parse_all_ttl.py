from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL
from collections import Counter

TTL_DIR = Path("allFilesTTL")  # folder you unzipped into

ttl_files = sorted(TTL_DIR.glob("*.ttl"))
if not ttl_files:
    raise SystemExit(f"No .ttl files found in {TTL_DIR.resolve()}")

g = Graph()
loaded = 0

for fp in ttl_files:
    try:
        g.parse(fp, format="turtle")
        loaded += 1
    except Exception as e:
        print(f"[WARN] Failed to parse {fp.name}: {e}")

print(f"Loaded {loaded}/{len(ttl_files)} TTL files")
print("Total triples:", len(g))

# Count rdf:type objects to sanity check what’s inside
type_counts = Counter(str(o) for o in g.objects(None, RDF.type))
print("\nTop rdf:type objects:")
for t, c in type_counts.most_common(20):
    print(f"{c:8d}  {t}")

# Classes can show up as owl:Class and/or rdfs:Class
owl_classes = set(g.subjects(RDF.type, OWL.Class))
rdfs_classes = set(g.subjects(RDF.type, RDFS.Class))
classes = owl_classes | rdfs_classes

print("\nClass counts:")
print("  owl:Class:", len(owl_classes))
print("  rdfs:Class:", len(rdfs_classes))
print("  union:", len(classes))

# Subclass edges
subclass_edges = set(g.triples((None, RDFS.subClassOf, None)))
print("\nSubclass edges:", len(subclass_edges))

# Print a few example classes with labels
print("\nSample classes with labels:")
shown = 0
for c in list(classes)[:50]:
    label = g.value(c, RDFS.label)
    if label is not None:
        print(" ", c, "->", label)
        shown += 1
    if shown >= 15:
        break