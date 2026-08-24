from pathlib import Path
from collections import Counter

from rdflib import Graph, RDF, RDFS, OWL


def load_all_ttl(ttl_dir: Path) -> Graph:
    ttl_files = sorted(ttl_dir.glob("*.ttl"))
    if not ttl_files:
        raise SystemExit(f"No .ttl files found in: {ttl_dir.resolve()}")

    g = Graph()
    loaded = 0

    for fp in ttl_files:
        try:
            g.parse(fp, format="turtle")
            loaded += 1
        except Exception as e:
            print(f"[WARN] Failed to parse {fp.name}: {e}")

    print(f"Loaded {loaded}/{len(ttl_files)} TTL files from {ttl_dir.resolve()}")
    return g


def main() -> None:
    # CHANGE THIS if your folder name differs
    ttl_dir = Path("allFilesTTL")

    g = load_all_ttl(ttl_dir)

    print("\n=== CORE STATS ===")
    print("Total triples:", len(g))

    # Classes: count both owl:Class and rdfs:Class (ATMONTO uses lots of rdfs:Class)
    owl_classes = set(g.subjects(RDF.type, OWL.Class))
    rdfs_classes = set(g.subjects(RDF.type, RDFS.Class))
    classes = owl_classes | rdfs_classes

    # Subclass edges
    subclass_edges = set(g.triples((None, RDFS.subClassOf, None)))

    print("\n=== TBOX STATS ===")
    print("owl:Class:", len(owl_classes))
    print("rdfs:Class:", len(rdfs_classes))
    print("Class union:", len(classes))
    print("Subclass edges (rdfs:subClassOf):", len(subclass_edges))

    # Properties to exclude from "individual" count
    properties = set(g.subjects(RDF.type, RDF.Property)) \
        | set(g.subjects(RDF.type, OWL.ObjectProperty)) \
        | set(g.subjects(RDF.type, OWL.DatatypeProperty)) \
        | set(g.subjects(RDF.type, OWL.AnnotationProperty))

    # Approx ABox individuals = typed subjects minus schema objects
    typed_subjects = set(g.subjects(RDF.type, None))
    individuals = typed_subjects - classes - properties

    print("\n=== ABOX STATS (APPROX) ===")
    print("Typed subjects total (subjects with rdf:type):", len(typed_subjects))
    print("Properties (RDF/OWL):", len(properties))
    print("Approx ABox individuals (typed - classes - properties):", len(individuals))

    # Top rdf:type counts (useful slide material)
    print("\n=== TOP rdf:type COUNTS (ABox signal) ===")
    type_counts = Counter(str(o) for o in g.objects(None, RDF.type))
    for t, c in type_counts.most_common(25):
        print(f"{c:10d}  {t}")

    # Sample labeled classes (optional nice sanity check)
    print("\n=== SAMPLE CLASSES WITH LABELS ===")
    shown = 0
    for c in classes:
        label = g.value(c, RDFS.label)
        if label is not None:
            print(" ", str(c), "->", str(label))
            shown += 1
            if shown >= 15:
                break


if __name__ == "__main__":
    main()