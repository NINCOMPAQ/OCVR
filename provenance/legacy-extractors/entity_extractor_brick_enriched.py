from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import json

from rdflib import Graph, RDF, RDFS, OWL
from rdflib.term import URIRef


TBOX_PATH = Path("brick_tbox.ttl")
ABOX_DIR = Path("brick_mortardata_models")
OUT_PATH = Path("brick_entities_enriched.jsonl")

BRICK = "https://brickschema.org/schema/Brick#"
REF = "https://brickschema.org/schema/Brick/ref#"

HAS_POINT = URIRef(f"{BRICK}hasPoint")
HAS_PART = URIRef(f"{BRICK}hasPart")
IS_PART_OF = URIRef(f"{BRICK}isPartOf")
FEEDS = URIRef(f"{BRICK}feeds")
IS_FED_BY = URIRef(f"{BRICK}isFedBy")
HAS_LOCATION = URIRef(f"{BRICK}hasLocation")
LOCATED_IN = URIRef(f"{BRICK}locatedIn")
HAS_EXTERNAL_REFERENCE = URIRef(f"{REF}hasExternalReference")

BRICK_EQUIPMENT = URIRef(f"{BRICK}Equipment")
BRICK_POINT = URIRef(f"{BRICK}Point")
BRICK_LOCATION = URIRef(f"{BRICK}Location")
BRICK_SPACE = URIRef(f"{BRICK}Space")
BRICK_SYSTEM = URIRef(f"{BRICK}System")
BRICK_COLLECTION = URIRef(f"{BRICK}Collection")

TYPE_CAP = 6
RELATION_CAP = 8
SMALL_RELATION_CAP = 4


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


def bucket_for_entity(closure_set: set[URIRef], direct_types: list[URIRef]) -> str:
    if BRICK_POINT in closure_set:
        return "point"
    if BRICK_SYSTEM in closure_set or BRICK_COLLECTION in closure_set:
        return "system"
    if BRICK_SPACE in closure_set or BRICK_LOCATION in closure_set:
        return "location"
    if BRICK_EQUIPMENT in closure_set:
        return "equipment"

    type_names = [prettify(local_name(str(t))).lower() for t in list(closure_set) + list(direct_types)]
    point_markers = ("sensor", "setpoint", "command", "status", "alarm", "parameter", "demand")
    equipment_markers = ("coil", "fan", "valve", "pump", "vav", "unit", "meter", "damper", "boiler", "chiller", "handler", "equipment")
    location_markers = ("room", "floor", "building", "space", "zone", "location")

    if any(any(marker in name for marker in point_markers) for name in type_names):
        return "point"
    if any(any(marker in name for marker in equipment_markers) for name in type_names):
        return "equipment"
    if any(any(marker in name for marker in location_markers) for name in type_names):
        return "location"
    return "other"


def object_labels(g: Graph, s: URIRef, p: URIRef, limit: int) -> list[str]:
    vals: list[str] = []
    for o in g.objects(s, p):
        if isinstance(o, URIRef):
            vals.append(get_best_label(g, o))
        else:
            vals.append(str(o))
        if len(vals) >= limit:
            break
    return vals


def inverse_subject_labels(g: Graph, p: URIRef, o: URIRef, limit: int) -> list[str]:
    vals: list[str] = []
    for s in g.subjects(p, o):
        if isinstance(s, URIRef):
            vals.append(get_best_label(g, s))
        if len(vals) >= limit:
            break
    return vals


def summarize_relation(prefix: str, values: list[str], total: int) -> str | None:
    if not values:
        return None
    suffix = ""
    if total > len(values):
        suffix = f" (and {total - len(values)} more)"
    return f"- {prefix}: {', '.join(values)}{suffix}"


def relation_summary(g: Graph, s: URIRef, p: URIRef, prefix: str, limit: int) -> str | None:
    total = sum(1 for _ in g.objects(s, p))
    values = object_labels(g, s, p, limit)
    return summarize_relation(prefix, values, total)


def inverse_relation_summary(g: Graph, p: URIRef, o: URIRef, prefix: str, limit: int) -> str | None:
    total = sum(1 for _ in g.subjects(p, o))
    values = inverse_subject_labels(g, p, o, limit)
    return summarize_relation(prefix, values, total)


def make_context_lines(g: Graph, s: URIRef, bucket: str) -> list[str]:
    lines: list[str] = []

    if bucket == "equipment":
        for item in [
            relation_summary(g, s, HAS_POINT, "has points", RELATION_CAP),
            relation_summary(g, s, HAS_PART, "has parts", SMALL_RELATION_CAP),
            relation_summary(g, s, IS_PART_OF, "part of", SMALL_RELATION_CAP),
            relation_summary(g, s, FEEDS, "feeds", SMALL_RELATION_CAP),
            relation_summary(g, s, IS_FED_BY, "is fed by", SMALL_RELATION_CAP),
            relation_summary(g, s, HAS_LOCATION, "has location", SMALL_RELATION_CAP),
            relation_summary(g, s, LOCATED_IN, "located in", SMALL_RELATION_CAP),
        ]:
            if item:
                lines.append(item)

    elif bucket == "point":
        for item in [
            inverse_relation_summary(g, HAS_POINT, s, "point of", SMALL_RELATION_CAP),
            relation_summary(g, s, IS_PART_OF, "part of", SMALL_RELATION_CAP),
        ]:
            if item:
                lines.append(item)
        ext_refs = sum(1 for _ in g.objects(s, HAS_EXTERNAL_REFERENCE))
        if ext_refs > 0:
            lines.append(f"- external reference: present ({ext_refs})")

    elif bucket == "location":
        for item in [
            relation_summary(g, s, HAS_PART, "has parts", SMALL_RELATION_CAP),
            relation_summary(g, s, IS_PART_OF, "part of", SMALL_RELATION_CAP),
            inverse_relation_summary(g, HAS_LOCATION, s, "location of", SMALL_RELATION_CAP),
            inverse_relation_summary(g, LOCATED_IN, s, "contains", SMALL_RELATION_CAP),
        ]:
            if item:
                lines.append(item)

    elif bucket == "system":
        for item in [
            relation_summary(g, s, HAS_PART, "has parts", SMALL_RELATION_CAP),
            relation_summary(g, s, IS_PART_OF, "part of", SMALL_RELATION_CAP),
            relation_summary(g, s, FEEDS, "feeds", SMALL_RELATION_CAP),
            relation_summary(g, s, IS_FED_BY, "is fed by", SMALL_RELATION_CAP),
            relation_summary(g, s, HAS_POINT, "has points", RELATION_CAP),
        ]:
            if item:
                lines.append(item)

    else:
        for item in [
            relation_summary(g, s, IS_PART_OF, "part of", SMALL_RELATION_CAP),
            relation_summary(g, s, HAS_PART, "has parts", SMALL_RELATION_CAP),
            relation_summary(g, s, HAS_POINT, "has points", SMALL_RELATION_CAP),
        ]:
            if item:
                lines.append(item)

    return lines


def make_card_text(label: str, building: str, types_closure: list[str], context_lines: list[str]) -> str:
    short_types = get_type_text(types_closure)
    parts = [
        f"Entity: {label}.",
        f"Building: {building}.",
        f"Types: {', '.join(short_types)}.",
    ]
    if context_lines:
        parts.append("Context:")
        parts.extend(context_lines)
    return " ".join(parts)


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
            bucket = bucket_for_entity(closure_set, direct_types)
            context_lines = make_context_lines(g, s, bucket)
            card_text = make_card_text(label, building, types_closure, context_lines)

            rec = {
                "iri": iri,
                "label": label,
                "building": building,
                "bucket": bucket,
                "types": types,
                "types_closure": types_closure,
                "card_text": card_text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1
            if written % 5000 == 0:
                print("Wrote", written)

    print(f"Done. Wrote {written} enriched Brick entities to {OUT_PATH.resolve()}")


if __name__ == "__main__":
    main()

