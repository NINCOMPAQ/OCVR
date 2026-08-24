from __future__ import annotations

from pathlib import Path
from collections import defaultdict, deque
import json

from rdflib import Graph, RDF, RDFS, OWL
from rdflib.term import URIRef, Literal


TTL_DIR = Path("allFilesTTL")
OUT_PATH = Path("entities_enriched.jsonl")

# Curated broader set, not "everything"
TARGET_TYPES = [
    "https://data.nasa.gov/ontologies/atmonto/NAS#InternationalAirport",
    "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
    "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
    "https://data.nasa.gov/ontologies/atmonto/NAS#PhysicalRunway",
    "https://data.nasa.gov/ontologies/atmonto/NAS#OperationalRunway",
    "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
    "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
    "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
]

CAP_PER_TYPE = 8000  # adjust upward if you want

LAT_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/general#latitude")
LON_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/general#longitude")
AIRPORT_LOC_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#airportLocation")
FIX_NAME_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/ATM#fixName")
FIX_ID_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/ATM#fixId")
FIX_TYPE_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/ATM#fixType")
HAS_RUNWAY_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#hasRunway")
RUNWAY_LEN_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#runwayLengthInFeet")
RUNWAY_WID_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#runwayWidthInFeet")

AIRPORT_NAME_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#airportName")
ICAO_CODE_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#icaoAirportCode")
TIMEZONE_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#withinTimezone")
UTC_OFFSET_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/NAS#hoursOffsetFromUTC")

VISIBILITY_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#limitedVisibilityDistance")
UNLIMITED_VIS_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#unlimitedVisibility")
WIND_DIR_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#windDirectionFixed")
DEWPOINT_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#dewpoint")
CLOUD_TYPE_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#cloudType")
WEATHER_INTENSITY_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#weatherIntensity")
WEATHER_PROXIMITY_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#weatherProximity")
TAF_REPORT_TYPE_PRED = URIRef("https://data.nasa.gov/ontologies/atmonto/data#tafReportType")


def load_all_ttl(ttl_dir: Path) -> Graph:
    ttl_files = sorted(ttl_dir.glob("*.ttl"))
    if not ttl_files:
        raise SystemExit(f"No .ttl files found in: {ttl_dir.resolve()}")

    g = Graph()
    for fp in ttl_files:
        g.parse(fp, format="turtle")

    print(f"Loaded {len(ttl_files)} TTL files from {ttl_dir.resolve()}")
    print("Total triples:", len(g))
    return g


def build_superclass_index(g: Graph) -> dict[URIRef, set[URIRef]]:
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


def get_best_label(g: Graph, s: URIRef) -> str | None:
    lab = g.value(s, RDFS.label)
    if lab is not None:
        return str(lab)
    return local_name(str(s))


def literal_values(g: Graph, s: URIRef, p: URIRef, limit: int = 5) -> list[str]:
    vals = []
    for o in g.objects(s, p):
        if isinstance(o, Literal):
            vals.append(str(o))
        else:
            vals.append(local_name(str(o)))
        if len(vals) >= limit:
            break
    return vals


def get_coords_direct(g: Graph, s: URIRef) -> tuple[str | None, str | None]:
    lat = g.value(s, LAT_PRED)
    lon = g.value(s, LON_PRED)
    return (str(lat) if lat is not None else None,
            str(lon) if lon is not None else None)


def get_coords_via_uri_neighbors(g: Graph, s: URIRef, hop_limit: int = 12) -> tuple[str | None, str | None]:
    # direct first
    lat, lon = get_coords_direct(g, s)
    if lat and lon:
        return lat, lon

    checked = 0
    for _, o in g.predicate_objects(s):
        if isinstance(o, URIRef):
            lat2, lon2 = get_coords_direct(g, o)
            if lat2 or lon2:
                return lat2, lon2
            checked += 1
            if checked >= hop_limit:
                break
    return None, None


def make_card_text(
    label: str | None,
    iri: str,
    types_closure: list[str],
    extras: list[str],
) -> str:
    name = label or iri
    short_types = [local_name(t) for t in types_closure[:10] if local_name(t) != "Thing"]
    parts = [f"{name}.", f"Types: {', '.join(short_types)}."]
    parts.extend(extras)
    return " ".join(p for p in parts if p.strip())


def main() -> None:
    g = load_all_ttl(TTL_DIR)

    owl_classes = set(g.subjects(RDF.type, OWL.Class))
    rdfs_classes = set(g.subjects(RDF.type, RDFS.Class))
    classes = owl_classes | rdfs_classes

    properties = set(g.subjects(RDF.type, RDF.Property)) \
        | set(g.subjects(RDF.type, OWL.ObjectProperty)) \
        | set(g.subjects(RDF.type, OWL.DatatypeProperty)) \
        | set(g.subjects(RDF.type, OWL.AnnotationProperty))

    parents = build_superclass_index(g)
    closure_cache: dict[URIRef, set[URIRef]] = {}

    target_type_uris = [URIRef(t) for t in TARGET_TYPES]
    per_type_written = defaultdict(int)

    typed_subjects = set(g.subjects(RDF.type, None))
    individuals = [
        s for s in typed_subjects
        if isinstance(s, URIRef) and s not in classes and s not in properties
    ]

    print("Typed subjects:", len(typed_subjects))
    print("Approx individuals:", len(individuals))

    written = 0
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for s in individuals:
            direct_types = [o for o in g.objects(s, RDF.type) if isinstance(o, URIRef)]
            if not direct_types:
                continue

            matched = None
            for dt in direct_types:
                if dt in target_type_uris:
                    matched = str(dt)
                    break
            if matched is None:
                continue

            if CAP_PER_TYPE is not None and per_type_written[matched] >= CAP_PER_TYPE:
                continue

            closure_set: set[URIRef] = set()
            for dt in direct_types:
                closure_set |= compute_type_closure(parents, dt, closure_cache)

            types = [str(t) for t in direct_types]
            types_closure = [str(t) for t in closure_set]

            label = get_best_label(g, s)
            iri = str(s)

            extras = []

            # Coordinates
            lat, lon = get_coords_via_uri_neighbors(g, s)
            if lat and lon:
                extras.append(f"Coordinates: latitude {lat}, longitude {lon}.")

            # Fix metadata
            fix_name = literal_values(g, s, FIX_NAME_PRED, limit=1)
            if fix_name:
                extras.append(f"Fix name: {fix_name[0]}.")
            fix_id = literal_values(g, s, FIX_ID_PRED, limit=1)
            if fix_id:
                extras.append(f"Fix ID: {fix_id[0]}.")
            fix_type = literal_values(g, s, FIX_TYPE_PRED, limit=2)
            if fix_type:
                extras.append(f"Fix type: {', '.join(fix_type)}.")

            # Airport metadata
            airport_name = literal_values(g, s, AIRPORT_NAME_PRED, limit=1)
            if airport_name:
                extras.append(f"Airport name: {airport_name[0]}.")

            icao_code = literal_values(g, s, ICAO_CODE_PRED, limit=1)
            if icao_code:
                extras.append(f"ICAO airport code: {icao_code[0]}.")

            timezone_vals = literal_values(g, s, TIMEZONE_PRED, limit=1)
            if timezone_vals:
                extras.append(f"Timezone: {timezone_vals[0]}.")

            utc_offset = literal_values(g, s, UTC_OFFSET_PRED, limit=1)
            if utc_offset:
                extras.append(f"UTC offset hours: {utc_offset[0]}.")

            airport_locs = list(g.objects(s, AIRPORT_LOC_PRED))
            if airport_locs:
                extras.append("Airport has explicit airportLocation link.")
                for loc in airport_locs[:1]:
                    if isinstance(loc, URIRef):
                        lat2, lon2 = get_coords_via_uri_neighbors(g, loc)
                        if lat2 and lon2:
                            extras.append(f"Airport coordinates: latitude {lat2}, longitude {lon2}.")

            # Weather metadata
            vis = literal_values(g, s, VISIBILITY_PRED, limit=1)
            if vis:
                extras.append(f"Visibility distance: {vis[0]}.")

            unlimited_vis = literal_values(g, s, UNLIMITED_VIS_PRED, limit=1)
            if unlimited_vis:
                extras.append(f"Unlimited visibility: {unlimited_vis[0]}.")

            wind_dir = literal_values(g, s, WIND_DIR_PRED, limit=1)
            if wind_dir:
                extras.append(f"Wind direction: {wind_dir[0]}.")

            dewpoint = literal_values(g, s, DEWPOINT_PRED, limit=1)
            if dewpoint:
                extras.append(f"Dewpoint: {dewpoint[0]}.")

            cloud_type = literal_values(g, s, CLOUD_TYPE_PRED, limit=2)
            if cloud_type:
                extras.append(f"Cloud type: {', '.join(cloud_type)}.")

            weather_intensity = literal_values(g, s, WEATHER_INTENSITY_PRED, limit=2)
            if weather_intensity:
                extras.append(f"Weather intensity: {', '.join(weather_intensity)}.")

            weather_proximity = literal_values(g, s, WEATHER_PROXIMITY_PRED, limit=2)
            if weather_proximity:
                extras.append(f"Weather proximity: {', '.join(weather_proximity)}.")

            taf_report_type = literal_values(g, s, TAF_REPORT_TYPE_PRED, limit=1)
            if taf_report_type:
                extras.append(f"TAF report type: {taf_report_type[0]}.")

            # Runway metadata
            runway_count = len(list(g.objects(s, HAS_RUNWAY_PRED)))
            if runway_count > 0:
                extras.append(f"Associated runways: {runway_count}.")
            runway_len = literal_values(g, s, RUNWAY_LEN_PRED, limit=1)
            if runway_len:
                extras.append(f"Runway length in feet: {runway_len[0]}.")
            runway_wid = literal_values(g, s, RUNWAY_WID_PRED, limit=1)
            if runway_wid:
                extras.append(f"Runway width in feet: {runway_wid[0]}.")

            card_text = make_card_text(label, iri, types_closure, extras)

            rec = {
                "iri": iri,
                "label": label,
                "types": types,
                "types_closure": types_closure,
                "card_text": card_text,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1
            per_type_written[matched] += 1

            if written % 5000 == 0:
                print("Wrote", written)

    print(f"\nDone. Wrote {written} entities to {OUT_PATH.resolve()}")
    print("\nPer-type written:")
    for t, c in sorted(per_type_written.items(), key=lambda x: -x[1]):
        print(c, t)


if __name__ == "__main__":
    main()