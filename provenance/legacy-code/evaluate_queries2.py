import time
from statistics import mean

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

COLLECTION = "atmonto_minilm_enriched"
TOP_K = 5

# Post-hoc config (tunable)
INITIAL_FETCH = 25
FETCH_STEP = 25
MAX_FETCH = 200

TESTS = [
    {
        "name": "Waypoints near JFK",
        "query": "navigation waypoint near JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Arrival fixes for JFK",
        "query": "arrival fixes for JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
            "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix",
        ],
    },
    {
        "name": "Route segments near JFK",
        "query": "arrival route segment near JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Route leg on J37",
        "query": "route leg on J37",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment",
        ],
    },
    {
        "name": "Current weather at JFK",
        "query": "current weather at JFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Surface observation for KEWR",
        "query": "surface observation for KEWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#METARreport",
        ],
    },
    {
        "name": "Forecast weather for EWR",
        "query": "forecast weather for EWR",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Terminal forecast for KJFK",
        "query": "terminal forecast for KJFK",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/data#TAFmeteorologicalCondition",
        ],
    },
    {
        "name": "Airport code NY94",
        "query": "airport code NY94",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
    {
        "name": "Airport in America New York timezone",
        "query": "airport in America New York timezone",
        "constraint_any": [
            "https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        ],
    },
]


# -------------------------
# Core helpers
# -------------------------

def embed_query(model, query):
    return model.encode([query], normalize_embeddings=True)[0].tolist()


def is_relevant(hit, target_types):
    payload = hit.payload or {}
    closure = payload.get("types_closure", [])
    direct = payload.get("types", [])

    closure_set = set(closure)
    direct_set = set(direct)
    target_set = set(target_types)

    return bool((closure_set & target_set) or (direct_set & target_set))


def evaluate_hits(hits, target_types, k=TOP_K):
    relevant_flags = [is_relevant(h, target_types) for h in hits]
    relevant_count = sum(relevant_flags)

    valid_at_k = relevant_count / k if k > 0 else 0.0
    scores = [h.score for h in hits]
    avg_score_at_k = mean(scores) if scores else 0.0

    return relevant_flags, relevant_count, valid_at_k, avg_score_at_k


# -------------------------
# Retrieval modes
# -------------------------

def run_query_unconstrained(client, qvec):
    start = time.perf_counter()

    hits = client.query_points(
        collection_name=COLLECTION,
        query=qvec,
        limit=TOP_K,
        with_payload=True,
    ).points

    elapsed = time.perf_counter() - start
    return hits, elapsed


def run_query_prehoc(client, qvec, target_types):
    start = time.perf_counter()

    hits = client.query_points(
        collection_name=COLLECTION,
        query=qvec,
        limit=TOP_K,
        with_payload=True,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="types_closure",
                    match=MatchAny(any=target_types)
                )
            ]
        ),
    ).points

    elapsed = time.perf_counter() - start
    return hits, elapsed


def run_query_posthoc(client, qvec, target_types):
    start = time.perf_counter()

    accepted = []
    accepted_ids = set()

    fetched = 0
    current_limit = INITIAL_FETCH
    total_examined = 0
    batches = 0

    while current_limit <= MAX_FETCH and len(accepted) < TOP_K:
        hits = client.query_points(
            collection_name=COLLECTION,
            query=qvec,
            limit=current_limit,
            with_payload=True,
        ).points

        batches += 1

        new_hits = hits[total_examined:]
        total_examined = len(hits)

        for hit in new_hits:
            iri = (hit.payload or {}).get("iri")

            if iri in accepted_ids:
                continue

            if is_relevant(hit, target_types):
                accepted.append(hit)
                accepted_ids.add(iri)

                if len(accepted) == TOP_K:
                    break

        if len(hits) < current_limit:
            break

        current_limit += FETCH_STEP

    elapsed = time.perf_counter() - start
    return accepted[:TOP_K], elapsed, total_examined, batches


# -------------------------
# Main evaluation
# -------------------------

def main():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = QdrantClient(url="http://localhost:6333")

    stats = {
        "uncon": [],
        "pre": [],
        "post": [],
    }

    times = {
        "uncon": 0.0,
        "pre": 0.0,
        "post": 0.0,
    }

    posthoc_examined = []
    posthoc_batches = []

    for test in TESTS:
        name = test["name"]
        query = test["query"]
        target_types = test["constraint_any"]

        print("\n" + "#" * 100)
        print(f"TEST: {name}")
        print("#" * 100)

        qvec = embed_query(model, query)

        # Unconstrained
        hits_u, t_u = run_query_unconstrained(client, qvec)
        _, _, v_u, s_u = evaluate_hits(hits_u, target_types)

        # Pre-hoc
        hits_p, t_p = run_query_prehoc(client, qvec, target_types)
        _, _, v_p, s_p = evaluate_hits(hits_p, target_types)

        # Post-hoc
        hits_ph, t_ph, examined, batches = run_query_posthoc(client, qvec, target_types)
        _, _, v_ph, s_ph = evaluate_hits(hits_ph, target_types)

        # Store
        stats["uncon"].append((v_u, s_u))
        stats["pre"].append((v_p, s_p))
        stats["post"].append((v_ph, s_ph))

        times["uncon"] += t_u
        times["pre"] += t_p
        times["post"] += t_ph

        posthoc_examined.append(examined)
        posthoc_batches.append(batches)

        # Print per test
        print(f"UNCONSTRAINED: valid@5={v_u:.2f}, score={s_u:.4f}, time={t_u:.4f}")
        print(f"PRE-HOC:       valid@5={v_p:.2f}, score={s_p:.4f}, time={t_p:.4f}")
        print(f"POST-HOC:      valid@5={v_ph:.2f}, score={s_ph:.4f}, time={t_ph:.4f}, examined={examined}, batches={batches}")

    # -------------------------
    # Overall summary
    # -------------------------

    def unpack(vals):
        return [v for v, _ in vals], [s for _, s in vals]

    u_v, u_s = unpack(stats["uncon"])
    p_v, p_s = unpack(stats["pre"])
    ph_v, ph_s = unpack(stats["post"])

    print("\n" + "=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)

    print(f"Unconstrained valid@5: {mean(u_v):.4f}")
    print(f"Pre-hoc valid@5:       {mean(p_v):.4f}")
    print(f"Post-hoc valid@5:      {mean(ph_v):.4f}")

    print(f"\nUnconstrained score: {mean(u_s):.4f}")
    print(f"Pre-hoc score:       {mean(p_s):.4f}")
    print(f"Post-hoc score:      {mean(ph_s):.4f}")

    print(f"\nAvg time unconstrained: {times['uncon']/len(TESTS):.4f}")
    print(f"Avg time pre-hoc:       {times['pre']/len(TESTS):.4f}")
    print(f"Avg time post-hoc:      {times['post']/len(TESTS):.4f}")

    print(f"\nPost-hoc avg candidates examined: {mean(posthoc_examined):.2f}")
    print(f"Post-hoc avg batches:             {mean(posthoc_batches):.2f}")


if __name__ == "__main__":
    main()