from __future__ import annotations

from collections import Counter, defaultdict, deque
from html import unescape
import json
import os
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SPARQL_ENDPOINT = "https://dbpedia.org/sparql"
OUT_PATH = Path(os.environ.get("DBPEDIA_OUT_PATH", "dbpedia_us_civic_places_entities_enriched.jsonl"))

DBO = "http://dbpedia.org/ontology/"
DBR_US = "http://dbpedia.org/resource/United_States"

DEFAULT_TARGET_CLASSES = [
    "EducationalInstitution",
    "University",
    "School",
    "City",
    "Town",
    "Village",
    "ArchitecturalStructure",
    "Building",
    "ReligiousBuilding",
    "Infrastructure",
    "Dam",
    "Venue",
    "Stadium",
    "Library",
    "Hospital",
]

env_classes = os.environ.get("DBPEDIA_TARGET_CLASSES")
TARGET_CLASSES = [part.strip() for part in env_classes.split(",") if part.strip()] if env_classes else DEFAULT_TARGET_CLASSES
TARGET_TYPES = [f"{DBO}{name}" for name in TARGET_CLASSES]

BATCH_LIMIT = 500
ENRICH_BATCH_SIZE = int(os.environ.get("DBPEDIA_ENRICH_BATCH_SIZE", "40") or "40")
REQUEST_SLEEP_SEC = 0.2
MAX_RETRIES = 4
USER_AGENT = "OntologyExperiment/0.1 (DBpedia US Civic Places)"
MAX_PER_CLASS = int(os.environ.get("DBPEDIA_MAX_PER_CLASS", "0") or "0")
MAX_TOTAL_ENTITIES = int(os.environ.get("DBPEDIA_MAX_TOTAL_ENTITIES", "0") or "0")
SKIP_FACT_ENRICHMENT = os.environ.get("DBPEDIA_SKIP_FACT_ENRICHMENT", "").lower() in {"1", "true", "yes"}

ABSTRACT_CAP = 420
LITERAL_CAP = 3
OBJECT_CAP = 4

PREFERRED_LITERAL_PROPS = {
    f"{DBO}motto": "motto",
    f"{DBO}foundingDate": "founded",
    f"{DBO}foundingYear": "founded",
    f"{DBO}openingDate": "opened",
    f"{DBO}date": "date",
    f"{DBO}populationTotal": "population",
    f"{DBO}elevation": "elevation",
    f"{DBO}areaTotal": "area",
    f"{DBO}numberOfStudents": "students",
    f"{DBO}facultySize": "faculty size",
    f"{DBO}campus": "campus",
    f"{DBO}religion": "religion",
    f"{DBO}height": "height",
    f"{DBO}buildingStartDate": "construction started",
    f"{DBO}buildingEndDate": "construction ended",
    f"{DBO}length": "length",
    f"{DBO}installedCapacity": "installed capacity",
}

PREFERRED_OBJECT_PROPS = {
    f"{DBO}city": "city",
    f"{DBO}state": "state",
    f"{DBO}location": "location",
    f"{DBO}county": "county",
    f"{DBO}nearestCity": "nearest city",
    f"{DBO}owner": "owner",
    f"{DBO}operator": "operator",
    f"{DBO}affiliation": "affiliation",
    f"{DBO}campus": "campus",
    f"{DBO}architect": "architect",
    f"{DBO}tenant": "tenant",
    f"{DBO}river": "river",
}


def sparql(query: str) -> dict[str, Any]:
    url = SPARQL_ENDPOINT + "?" + urlencode({"query": query, "format": "application/sparql-results+json"})
    req = Request(
        url,
        headers={
            "Accept": "application/sparql-results+json",
            "User-Agent": USER_AGENT,
        },
    )

    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            last_err = exc
            wait = min(2 ** attempt, 20)
            print(f"SPARQL request failed on attempt {attempt}/{MAX_RETRIES}: {exc}. Retrying in {wait}s...")
            time.sleep(wait)

    raise RuntimeError(f"SPARQL request failed after {MAX_RETRIES} attempts: {last_err}")


def value(binding: dict[str, Any], key: str) -> str | None:
    item = binding.get(key)
    if item is None:
        return None
    return item.get("value")


def literal(binding: dict[str, Any], key: str) -> str | None:
    val = value(binding, key)
    if val is None:
        return None
    return unescape(val).strip()


def local_name(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


def prettify_name(iri_or_name: str) -> str:
    return local_name(iri_or_name).replace("_", " ")


def short_abstract(text: str | None) -> str | None:
    if not text:
        return None
    clean = " ".join(text.split())
    if len(clean) <= ABSTRACT_CAP:
        return clean
    return clean[:ABSTRACT_CAP].rsplit(" ", 1)[0] + "..."


def fetch_subclass_parents() -> dict[str, set[str]]:
    query = f"""
PREFIX dbo: <{DBO}>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?child ?parent WHERE {{
  ?child rdfs:subClassOf ?parent .
  FILTER(STRSTARTS(STR(?child), STR(dbo:)))
}}
"""
    rows = sparql(query)["results"]["bindings"]
    parents: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        child = value(row, "child")
        parent = value(row, "parent")
        if child and parent:
            parents[child].add(parent)
    print("Subclass edges:", sum(len(v) for v in parents.values()))
    return parents


def type_closure(parents: dict[str, set[str]], direct_types: list[str]) -> list[str]:
    seen: set[str] = set()
    dq: deque[str] = deque(direct_types)
    while dq:
        cur = dq.popleft()
        if cur in seen:
            continue
        seen.add(cur)
        for parent in parents.get(cur, ()):
            if parent not in seen:
                dq.append(parent)
    return sorted(seen)


def fetch_entities_for_class(class_iri: str) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    offset = 0
    batch_limit = min(BATCH_LIMIT, MAX_PER_CLASS) if MAX_PER_CLASS else BATCH_LIMIT

    while True:
        query = f"""
PREFIX dbo: <{DBO}>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?s ?label ?abstract WHERE {{
  ?s a <{class_iri}> ;
     dbo:country dbr:United_States .
  OPTIONAL {{ ?s rdfs:label ?label . FILTER(LANG(?label) = "en") }}
  OPTIONAL {{ ?s dbo:abstract ?abstract . FILTER(LANG(?abstract) = "en") }}
  OPTIONAL {{ ?s dbo:city ?city . OPTIONAL {{ ?city rdfs:label ?cityLabel . FILTER(LANG(?cityLabel) = "en") }} }}
  OPTIONAL {{ ?s dbo:state ?state . OPTIONAL {{ ?state rdfs:label ?stateLabel . FILTER(LANG(?stateLabel) = "en") }} }}
  OPTIONAL {{ ?s dbo:location ?location . OPTIONAL {{ ?location rdfs:label ?locationLabel . FILTER(LANG(?locationLabel) = "en") }} }}
}}
ORDER BY ?s
LIMIT {batch_limit}
OFFSET {offset}
"""
        rows = sparql(query)["results"]["bindings"]
        if not rows:
            break

        for row in rows:
            iri = value(row, "s")
            if not iri:
                continue
            entities.append(
                {
                    "iri": iri,
                    "label": literal(row, "label") or prettify_name(iri),
                    "abstract": literal(row, "abstract"),
                    "city": literal(row, "cityLabel") or (prettify_name(value(row, "city")) if value(row, "city") else None),
                    "state": literal(row, "stateLabel") or (prettify_name(value(row, "state")) if value(row, "state") else None),
                    "location": literal(row, "locationLabel") or (prettify_name(value(row, "location")) if value(row, "location") else None),
                }
            )

        print(f"Fetched {len(entities)} {prettify_name(class_iri)} entities...")
        if MAX_PER_CLASS and len(entities) >= MAX_PER_CLASS:
            return entities[:MAX_PER_CLASS]
        offset += batch_limit
        time.sleep(REQUEST_SLEEP_SEC)

    return entities


def fetch_direct_types(iris: list[str]) -> dict[str, list[str]]:
    if not iris:
        return {}

    values_clause = " ".join(f"<{iri}>" for iri in iris)
    query = f"""
PREFIX dbo: <{DBO}>
SELECT DISTINCT ?s ?type WHERE {{
  VALUES ?s {{ {values_clause} }}
  ?s a ?type .
  FILTER(STRSTARTS(STR(?type), STR(dbo:)))
}}
ORDER BY ?s ?type
"""
    rows = sparql(query)["results"]["bindings"]
    out: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        iri = value(row, "s")
        t = value(row, "type")
        if iri and t:
            out[iri].append(t)
    return dict(out)


def fetch_literals(iris: list[str]) -> dict[str, list[str]]:
    if not iris:
        return {}

    values_clause = " ".join(f"<{iri}>" for iri in iris)
    prop_values = " ".join(f"<{p}>" for p in PREFERRED_LITERAL_PROPS)
    query = f"""
SELECT ?s ?p ?o WHERE {{
  VALUES ?s {{ {values_clause} }}
  VALUES ?p {{ {prop_values} }}
  ?s ?p ?o .
  FILTER(isLiteral(?o))
}}
ORDER BY ?s ?p ?o
"""
    rows = sparql(query)["results"]["bindings"]
    out: dict[str, list[str]] = defaultdict(list)
    seen_counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        iri = value(row, "s")
        prop = value(row, "p")
        obj = literal(row, "o")
        if not iri or not prop or not obj:
            continue
        key = (iri, prop)
        if seen_counts[key] >= LITERAL_CAP:
            continue
        seen_counts[key] += 1
        out[iri].append(f"{PREFERRED_LITERAL_PROPS.get(prop, prettify_name(prop))}: {obj}")
    return dict(out)


def fetch_objects(iris: list[str]) -> dict[str, list[str]]:
    if not iris:
        return {}

    values_clause = " ".join(f"<{iri}>" for iri in iris)
    prop_values = " ".join(f"<{p}>" for p in PREFERRED_OBJECT_PROPS)
    query = f"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?s ?p ?o ?label WHERE {{
  VALUES ?s {{ {values_clause} }}
  VALUES ?p {{ {prop_values} }}
  ?s ?p ?o .
  FILTER(isIRI(?o))
  OPTIONAL {{ ?o rdfs:label ?label . FILTER(LANG(?label) = "en") }}
}}
ORDER BY ?s ?p ?o
"""
    rows = sparql(query)["results"]["bindings"]
    out: dict[str, list[str]] = defaultdict(list)
    seen_counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        iri = value(row, "s")
        prop = value(row, "p")
        obj_iri = value(row, "o")
        label = literal(row, "label")
        if not iri or not prop or not obj_iri:
            continue
        key = (iri, prop)
        if seen_counts[key] >= OBJECT_CAP:
            continue
        seen_counts[key] += 1
        obj_text = label or prettify_name(obj_iri)
        out[iri].append(f"{PREFERRED_OBJECT_PROPS.get(prop, prettify_name(prop))}: {obj_text}")
    return dict(out)


def make_card_text(
    label: str,
    target_classes: list[str],
    types_closure: list[str],
    abstract: str | None,
    facts: list[str],
) -> str:
    type_names = []
    seen = set()
    for t in target_classes + types_closure:
        name = prettify_name(t)
        if name in {"Thing", "Agent"}:
            continue
        if name not in seen:
            seen.add(name)
            type_names.append(name)
        if len(type_names) >= 8:
            break

    parts = [
        f"Entity: {label}.",
        "Country: United States.",
        f"Types: {', '.join(type_names)}.",
    ]
    abst = short_abstract(abstract)
    if abst:
        parts.append(f"Abstract: {abst}")
    if facts:
        parts.append("Context:")
        parts.extend(f"- {fact}." for fact in facts[:12])
    return " ".join(parts)


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def main() -> None:
    parents = fetch_subclass_parents()

    by_iri: dict[str, dict[str, Any]] = {}
    matched_targets: dict[str, set[str]] = defaultdict(set)

    for class_iri in TARGET_TYPES:
        print(f"\nFetching target class: {class_iri}")
        for ent in fetch_entities_for_class(class_iri):
            iri = ent["iri"]
            by_iri.setdefault(iri, ent)
            matched_targets[iri].add(class_iri)

    iris = sorted(by_iri)
    if MAX_TOTAL_ENTITIES:
        iris = iris[:MAX_TOTAL_ENTITIES]
    print(f"\nUnique direct-country entities before enrichment: {len(iris)}")

    all_types: dict[str, list[str]] = {}
    all_literals: dict[str, list[str]] = {}
    all_objects: dict[str, list[str]] = {}

    for n, batch in enumerate(chunks(iris, ENRICH_BATCH_SIZE), start=1):
        print(f"Enriching batch {n} ({len(batch)} entities)...")
        all_types.update(fetch_direct_types(batch))
        if not SKIP_FACT_ENRICHMENT:
            all_literals.update(fetch_literals(batch))
            all_objects.update(fetch_objects(batch))
        time.sleep(REQUEST_SLEEP_SEC)

    direct_type_counts: Counter[str] = Counter()
    closure_counts: Counter[str] = Counter()
    missing_label = 0
    sparse_cards = 0

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for iri in iris:
            ent = by_iri[iri]
            label = ent.get("label") or prettify_name(iri)
            if not ent.get("label"):
                missing_label += 1

            direct_types = sorted(set(all_types.get(iri, [])))
            if not direct_types:
                direct_types = sorted(matched_targets[iri])
            closure = type_closure(parents, direct_types)
            target_classes = sorted(matched_targets[iri])

            for t in target_classes:
                direct_type_counts[t] += 1
            for t in closure:
                closure_counts[t] += 1

            location_facts = []
            for key in ["city", "state", "location"]:
                if ent.get(key):
                    location_facts.append(f"{key}: {ent[key]}")
            facts = location_facts + all_objects.get(iri, []) + all_literals.get(iri, [])
            card_text = make_card_text(label, target_classes, closure, ent.get("abstract"), facts)
            if len(card_text) < 120:
                sparse_cards += 1

            rec = {
                "iri": iri,
                "label": label,
                "country": DBR_US,
                "target_classes": target_classes,
                "types": direct_types,
                "types_closure": closure,
                "card_text": card_text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nDone. Wrote {len(iris)} DBpedia US Civic Places entities to {OUT_PATH.resolve()}")
    print("\nTarget class counts:")
    for t, count in direct_type_counts.most_common():
        print(count, t)
    print("\nSelected closure counts:")
    for t in TARGET_TYPES + [f"{DBO}EducationalInstitution", f"{DBO}Organisation", f"{DBO}Place"]:
        if closure_counts[t]:
            print(closure_counts[t], t)
    print("\nQuality:")
    print("missing_label:", missing_label)
    print("sparse_card_text:", sparse_cards)


if __name__ == "__main__":
    main()
