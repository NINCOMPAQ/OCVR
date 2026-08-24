import time
from statistics import mean

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

COLLECTION = "atmonto_minilm_enriched"
TOP_K = 5

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


def run_query(client, model, query, constraint_any=None, limit=TOP_K):
    qvec = model.encode([query], normalize_embeddings=True)[0].tolist()

    kwargs = {
        "collection_name": COLLECTION,
        "query": qvec,
        "limit": limit,
        "with_payload": True,
    }

    if constraint_any:
        kwargs["query_filter"] = Filter(
            must=[
                FieldCondition(
                    key="types_closure",
                    match=MatchAny(any=constraint_any)
                )
            ]
        )

    start = time.perf_counter()
    hits = client.query_points(**kwargs).points
    elapsed = time.perf_counter() - start
    return hits, elapsed


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


def print_hits(title, hits, relevant_flags):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

    for i, (hit, rel) in enumerate(zip(hits, relevant_flags), 1):
        p = hit.payload or {}
        print(f"\nResult {i}")
        print("Score:", hit.score)
        print("Relevant:", rel)
        print("Label:", p.get("label"))
        print("IRI:", p.get("iri"))
        print("Types:", p.get("types"))


def main():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = QdrantClient(url="http://localhost:6333")

    summary_rows = []

    unconstrained_valids = []
    constrained_valids = []
    unconstrained_avg_scores = []
    constrained_avg_scores = []

    total_unconstrained_time = 0.0
    total_constrained_time = 0.0

    for test in TESTS:
        name = test["name"]
        query = test["query"]
        target_types = test["constraint_any"]

        unconstrained_hits, unconstrained_time = run_query(
            client, model, query, constraint_any=None, limit=TOP_K
        )
        constrained_hits, constrained_time = run_query(
            client, model, query, constraint_any=target_types, limit=TOP_K
        )

        total_unconstrained_time += unconstrained_time
        total_constrained_time += constrained_time

        uncon_rel_flags, uncon_rel_count, uncon_valid, uncon_avg_score = evaluate_hits(
            unconstrained_hits, target_types, k=TOP_K
        )
        con_rel_flags, con_rel_count, con_valid, con_avg_score = evaluate_hits(
            constrained_hits, target_types, k=TOP_K
        )

        unconstrained_valids.append(uncon_valid)
        constrained_valids.append(con_valid)
        unconstrained_avg_scores.append(uncon_avg_score)
        constrained_avg_scores.append(con_avg_score)

        print("\n" + "#" * 100)
        print(f"TEST: {name}")
        print(f"Query: {query}")
        print(f"Target types: {target_types}")
        print("#" * 100)

        print(f"\nUNCONSTRAINED relevant_count@{TOP_K}: {uncon_rel_count}")
        print(f"UNCONSTRAINED valid@{TOP_K}: {uncon_valid:.2f}")
        print(f"UNCONSTRAINED avg_score@{TOP_K}: {uncon_avg_score:.4f}")
        print(f"UNCONSTRAINED query_time_sec: {unconstrained_time:.4f}")

        print(f"\nCONSTRAINED relevant_count@{TOP_K}: {con_rel_count}")
        print(f"CONSTRAINED valid@{TOP_K}: {con_valid:.2f}")
        print(f"CONSTRAINED avg_score@{TOP_K}: {con_avg_score:.4f}")
        print(f"CONSTRAINED query_time_sec: {constrained_time:.4f}")

        print_hits(f"{name} | UNCONSTRAINED", unconstrained_hits, uncon_rel_flags)
        print_hits(f"{name} | CONSTRAINED", constrained_hits, con_rel_flags)

        summary_rows.append({
            "name": name,
            "query": query,
            "unconstrained_relevant_count_at_k": uncon_rel_count,
            "unconstrained_valid_at_k": uncon_valid,
            "unconstrained_avg_score_at_k": uncon_avg_score,
            "unconstrained_time_sec": unconstrained_time,
            "constrained_relevant_count_at_k": con_rel_count,
            "constrained_valid_at_k": con_valid,
            "constrained_avg_score_at_k": con_avg_score,
            "constrained_time_sec": constrained_time,
        })

    print("\n" + "=" * 100)
    print("SUMMARY PER QUERY")
    print("=" * 100)
    for row in summary_rows:
        print(
            f"{row['name']}: "
            f"unconstrained valid@{TOP_K}={row['unconstrained_valid_at_k']:.2f}, "
            f"unconstrained avg_score@{TOP_K}={row['unconstrained_avg_score_at_k']:.4f}, "
            f"unconstrained time={row['unconstrained_time_sec']:.4f}s | "
            f"constrained valid@{TOP_K}={row['constrained_valid_at_k']:.2f}, "
            f"constrained avg_score@{TOP_K}={row['constrained_avg_score_at_k']:.4f}, "
            f"constrained time={row['constrained_time_sec']:.4f}s"
        )

    print("\n" + "=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)
    print(f"Mean unconstrained valid@{TOP_K}: {mean(unconstrained_valids):.4f}")
    print(f"Mean constrained valid@{TOP_K}:   {mean(constrained_valids):.4f}")
    print(f"Mean unconstrained avg_score@{TOP_K}: {mean(unconstrained_avg_scores):.4f}")
    print(f"Mean constrained avg_score@{TOP_K}:   {mean(constrained_avg_scores):.4f}")
    print(f"Total unconstrained query time (sec): {total_unconstrained_time:.4f}")
    print(f"Total constrained query time (sec):   {total_constrained_time:.4f}")
    print(f"Average unconstrained query time (sec): {total_unconstrained_time / len(TESTS):.4f}")
    print(f"Average constrained query time (sec):   {total_constrained_time / len(TESTS):.4f}")


if __name__ == "__main__":
    main()