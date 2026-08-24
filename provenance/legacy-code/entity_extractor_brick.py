from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import json

from rdflib import Graph, RDF, RDFS, OWL
from rdflib.term import URIRef


TBOX_PATH = Path("brick_tbox.ttl")
ABOX_DIR = Path("brick_mortardata_models")
OUT_PATH = Path("brick_entities.jsonl")

BRICK = "https://brickschema.org/schema/Brick#"
REF = "https://brickschema.org/schema/Brick/ref#"

TYPE_CAP = 6


def load_graphs(tbox_path: Path, abox_dir: Path) -> tuple[Graph, dict[URIRef, str], set[URIRef]]:
    if not tbox_path.exists():
        raise SystemExit(f"Missing TBox file: {tbox_path.resolve()}")
    abox_files = sorted(abox_dir.glob("*.ttl"))
    if not abox_files:
        raise SystemExit(f"No ABox .ttl files found in: {abox_dir.resolve()}")

    g = Graph()
    g.parse(tbox_path, format="turtle")

    subject_building: dict[URIRef, str] = {}
    abox_subjects: set[URIRef] = set()

    for fp in abox_files:
        building = fp.stem
        subg = Graph()
        subg.parse(fp, format="turtle")
        for s in subg.subjects():
            if isinstance(s, URIRef):
                subject_building.setdefault(s, building)
                abox_subjects.add(s)
        for triple in subg:
            g.add(triple)

    print(f"Loaded TBox: {tbox_path.resolve()}")
    print(f"Loaded {len(abox_files)} Brick ABox files from {abox_dir.resolve()}")
    print("Total triples:", len(g))
    print("ABox URI subjects:", len(abox_subjects))
    return g, subject_building, abox_subjects


def build_superclass_index(g: Graph) -> dict[URIRef, set[URIRef]]:
    parents: dict[URIRef, set[URIRef]] = defaultdict(set)
    for child, _, parent in g.triples((None, RDFS.subClassOf, None)):
        if isinstance(child, URIRef) and isinstance(parent, URIRef):
            parents[child].add(parent)
    return parents


def compute_type_closure(
    parents: dict[URIRef, set[URIRef]],
    t: URIRef,
    cache: dict[URIRef, set[URIRef]],
) -> set[URIRef]:
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


def local_name(u: str) -> str:
    if "#" in u:
        return u.split("#")[-1]
    return u.rstrip("/").split("/")[-1]


def prettify(name: str) -> str:
    return name.replace("_", " ")


def get_best_label(g: Graph, s: URIRef) -> str:
    lab = g.value(s, RDFS.label)
    if lab is not None:
        return str(lab)
    return local_name(str(s))


def get_type_text(types_closure: list[str]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for t in types_closure:
        short = prettify(local_name(t))
        if short in {"Thing", "Class", "Entity", "Resource", "Asset"}:
            continue
        if short not in seen:
            seen.add(short)
            names.append(short)
        if len(names) >= TYPE_CAP:
            break
    return names


def make_card_text(label: str, building: str, types_closure: list[str]) -> str:
    short_types = get_type_text(types_closure)
    return f"Entity: {label}. Building: {building}. Types: {', '.join(short_types)}."


def main() -> None:
    g, subject_building, abox_subjects = load_graphs(TBOX_PATH, ABOX_DIR)

    owl_classes = set(g.subjects(RDF.type, OWL.Class))
    rdfs_classes = set(g.subjects(RDF.type, RDFS.Class))
    classes = owl_classes | rdfs_classes

    properties = set(g.subjects(RDF.type, RDF.Property)) \
        | set(g.subjects(RDF.type, OWL.ObjectProperty)) \
        | set(g.subjects(RDF.type, OWL.DatatypeProperty)) \
        | set(g.subjects(RDF.type, OWL.AnnotationProperty))

    parents = build_superclass_index(g)
    closure_cache: dict[URIRef, set[URIRef]] = {}

    typed_subjects = set(g.subjects(RDF.type, None))
    individuals = [
        s for s in typed_subjects
        if isinstance(s, URIRef)
        and s in abox_subjects
        and s not in classes
        and s not in properties
        and not str(s).startswith(BRICK)
        and not str(s).startswith(REF)
    ]

    written = 0
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for s in individuals:
            direct_types = [o for o in g.objects(s, RDF.type) if isinstance(o, URIRef)]
            if not direct_types:
                continue

            closure_set: set[URIRef] = set()
            for dt in direct_types:
                closure_set |= compute_type_closure(parents, dt, closure_cache)

            types = [str(t) for t in direct_types]
            types_closure = sorted(str(t) for t in closure_set)
            label = get_best_label(g, s)
            iri = str(s)
            building = subject_building.get(s, "unknown")
            card_text = make_card_text(label, building, types_closure)

            rec = {
                "iri": iri,
                "label": label,
                "building": building,
                "types": types,
                "types_closure": types_closure,
                "card_text": card_text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1
            if written % 5000 == 0:
                print("Wrote", written)

    print(f"Done. Wrote {written} Brick entities to {OUT_PATH.resolve()}")


if __name__ == "__main__":
    main()

