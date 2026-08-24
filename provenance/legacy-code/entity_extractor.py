from __future__ import annotations

from pathlib import Path
from collections import defaultdict, deque
import json

from rdflib import Graph, RDF, RDFS, OWL
from rdflib.term import URIRef


TTL_DIR = Path("allFilesTTL")          # folder containing 29 TTL files
OUT_PATH = Path("entities.jsonl")      # output for embeddings step

# --- Optional: restrict to a few high-value types for v1 (recommended) ---
# Put full IRIs here. Leave empty list [] to extract ALL typed individuals (can be huge).
TARGET_TYPES: list[str] = [
    # Examples (replace/extend if you want):
    "https://data.nasa.gov/ontologies/atmonto/NAS#InternationalAirport",
    "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
    "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
    # "https://data.nasa.gov/ontologies/atmonto/NAS#TransitionRoute",
]

# Optional caps per target type so you don't write millions of entities on day 1
CAP_PER_TYPE = 20000  # set None for unlimited


def load_all_ttl(ttl_dir: Path) -> Graph:
    ttl_files = sorted(ttl_dir.glob("*.ttl"))
    if not ttl_files:
        raise SystemExit(f"No .ttl files found in: {ttl_dir.resolve()}")

    g = Graph()
    loaded = 0
    for fp in ttl_files:
        g.parse(fp, format="turtle")
        loaded += 1

    print(f"Loaded {loaded}/{len(ttl_files)} TTL files from {ttl_dir.resolve()}")
    print("Total triples:", len(g))
    return g


def build_superclass_index(g: Graph) -> dict[URIRef, set[URIRef]]:
    """
    Returns mapping child_class -> set(parent_classes) from rdfs:subClassOf.
    """
    parents: dict[URIRef, set[URIRef]] = defaultdict(set)
    for child, _, parent in g.triples((None, RDFS.subClassOf, None)):
        if isinstance(child, URIRef) and isinstance(parent, URIRef):
            parents[child].add(parent)
    print("Subclass edges:", sum(len(v) for v in parents.values()))
    return parents


def compute_type_closure(
    parents: dict[URIRef, set[URIRef]],
    t: URIRef,
    cache: dict[URIRef, set[URIRef]],
) -> set[URIRef]:
    """
    Computes transitive closure of superclasses for a type t:
    closure(t) = {t} U all superclasses reachable via rdfs:subClassOf*
    """
    if t in cache:
        return cache[t]

    seen: set[URIRef] = set()
    dq: deque[URIRef] = deque([t])
    while dq:
        cur = dq.popleft()
        if cur in seen:
            continue
        seen.add(cur)
        for p in parents.get(cur, ()):
            if p not in seen:
                dq.append(p)

    cache[t] = seen
    return seen


def get_best_label(g: Graph, s: URIRef) -> str | None:
    """
    Prefer rdfs:label; fall back to local name from IRI.
    """
    lab = g.value(s, RDFS.label)
    if lab is not None:
        return str(lab)

    # localname fallback
    text = str(s)
    if "#" in text:
        return text.split("#")[-1]
    if "/" in text:
        return text.rstrip("/").split("/")[-1]
    return None


def make_card_text(label: str | None, iri: str, types_closure: list[str]) -> str:
    """
    Minimal 'entity card' text. Keep short for cheaper embeddings.
    """
    name = label or iri
    # Use shortened type names for readability in the embedded text
    short_types = []
    for t in types_closure[:12]:  # cap so text doesn't explode
        if "#" in t:
            short_types.append(t.split("#")[-1])
        else:
            short_types.append(t.split("/")[-1])
    return f"{name}. Types: {', '.join(short_types)}."


def main() -> None:
    g = load_all_ttl(TTL_DIR)

    # Build class sets (TBox-ish) so we can exclude them from individuals later
    owl_classes = set(g.subjects(RDF.type, OWL.Class))
    rdfs_classes = set(g.subjects(RDF.type, RDFS.Class))
    classes = owl_classes | rdfs_classes

    properties = set(g.subjects(RDF.type, RDF.Property)) \
        | set(g.subjects(RDF.type, OWL.ObjectProperty)) \
        | set(g.subjects(RDF.type, OWL.DatatypeProperty)) \
        | set(g.subjects(RDF.type, OWL.AnnotationProperty))

    parents = build_superclass_index(g)
    closure_cache: dict[URIRef, set[URIRef]] = {}

    # Target type URIs
    target_type_uris = [URIRef(t) for t in TARGET_TYPES]
    use_targets = len(target_type_uris) > 0

    # For caps
    per_type_written = defaultdict(int)

    typed_subjects = set(g.subjects(RDF.type, None))
    individuals = [
        s for s in typed_subjects
        if isinstance(s, URIRef) and s not in classes and s not in properties
    ]
    print("Typed subjects:", len(typed_subjects))
    print("Approx individuals (typed - classes - properties):", len(individuals))

    written = 0
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for s in individuals:
            # direct types of subject
            direct_types = [o for o in g.objects(s, RDF.type) if isinstance(o, URIRef)]
            if not direct_types:
                continue

            # If targeting, keep only subjects having at least one target type
            if use_targets:
                keep = False
                for dt in direct_types:
                    if dt in target_type_uris:
                        keep = True
                        break
                if not keep:
                    continue

            # Apply per-type cap (only meaningful when using TARGET_TYPES)
            if use_targets and CAP_PER_TYPE is not None:
                # Find the first matching target type (for counting)
                matched = None
                for dt in direct_types:
                    if dt in target_type_uris:
                        matched = str(dt)
                        break
                if matched is not None and per_type_written[matched] >= CAP_PER_TYPE:
                    continue

            # Compute types_closure = union of closures of each direct type
            closure_set: set[URIRef] = set()
            for dt in direct_types:
                closure_set |= compute_type_closure(parents, dt, closure_cache)

            types = [str(t) for t in direct_types]
            types_closure = [str(t) for t in closure_set]

            label = get_best_label(g, s)
            iri = str(s)
            card_text = make_card_text(label, iri, types_closure)

            rec = {
                "iri": iri,
                "label": label,
                "types": types,
                "types_closure": types_closure,
                "card_text": card_text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1

            if use_targets and CAP_PER_TYPE is not None:
                if matched is not None:
                    per_type_written[matched] += 1

            # progress
            if written % 5000 == 0:
                print("Wrote", written)

    print(f"\nDone. Wrote {written} entities to {OUT_PATH.resolve()}")
    if use_targets and CAP_PER_TYPE is not None:
        print("\nPer-type written:")
        for t, c in sorted(per_type_written.items(), key=lambda x: -x[1]):
            print(c, t)


if __name__ == "__main__":
    main()