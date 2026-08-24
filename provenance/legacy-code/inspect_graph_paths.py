from pathlib import Path
from rdflib import Graph, URIRef, RDFS

TTL_DIR = Path("allFilesTTL")

AIRPORT = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#NY94airport")
FIX = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#FixBUSCX")

g = Graph()
for fp in sorted(TTL_DIR.glob("*.ttl")):
    g.parse(fp, format="turtle")

def show_entity(entity: URIRef, max_triples: int = 60):
    print("\n" + "=" * 80)
    print("ENTITY:", entity)
    print("LABEL:", g.value(entity, RDFS.label))
    print("-" * 80)

    count = 0
    for p, o in g.predicate_objects(entity):
        print("DIRECT:", p, "->", o)
        count += 1
        if count >= max_triples:
            break

    print("\nOne-hop expansions for URI objects:")
    for p, o in g.predicate_objects(entity):
        if isinstance(o, URIRef):
            print(f"\n[{p}] -> {o}")
            shown = 0
            for p2, o2 in g.predicate_objects(o):
                print("   ", p2, "->", o2)
                shown += 1
                if shown >= 20:
                    break

show_entity(AIRPORT)
show_entity(FIX)