import time
from statistics import mean

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny
from benchmark_queries_brick import TESTS

COLLECTION = "brick_mortardata_minilm_enriched"
TOP_K = 5

POSTHOC_CAPS = [25, 100, 200, 400, 2000]
INITIAL_FETCH = 25
FETCH_STEP = 25


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
    success_at_k = 1.0 if relevant_count == k else 0.0

    return relevant_flags, relevant_count, valid_at_k, avg_score_at_k, success_at_k


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


def run_query_posthoc(client, qvec, target_types, max_fetch):
    start = time.perf_counter()

    accepted = []
    accepted_ids = set()

    current_limit = INITIAL_FETCH
    total_examined = 0
    batches = 0

    while current_limit <= max_fetch and len(accepted) < TOP_K:
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


def main():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = QdrantClient(url="http://localhost:6333")

    uncon_valids = []
    uncon_scores = []
    uncon_success = []
    uncon_time = 0.0

    pre_valids = []
    pre_scores = []
    pre_success = []
    pre_time = 0.0

    post_stats = {
        cap: {
            "valids": [],
            "scores": [],
            "success": [],
            "times": [],
            "examined": [],
            "batches": [],
        }
        for cap in POSTHOC_CAPS
    }

    for test in TESTS:
        query = test["query"]
        target_types = test["constraint_any"]

        qvec = embed_query(model, query)

        hits_u, t_u = run_query_unconstrained(client, qvec)
        _, _, v_u, s_u, succ_u = evaluate_hits(hits_u, target_types)
        uncon_valids.append(v_u)
        uncon_scores.append(s_u)
        uncon_success.append(succ_u)
        uncon_time += t_u

        hits_p, t_p = run_query_prehoc(client, qvec, target_types)
        _, _, v_p, s_p, succ_p = evaluate_hits(hits_p, target_types)
        pre_valids.append(v_p)
        pre_scores.append(s_p)
        pre_success.append(succ_p)
        pre_time += t_p

        for cap in POSTHOC_CAPS:
            hits_ph, t_ph, examined, batches = run_query_posthoc(client, qvec, target_types, max_fetch=cap)
            _, _, v_ph, s_ph, succ_ph = evaluate_hits(hits_ph, target_types)

            post_stats[cap]["valids"].append(v_ph)
            post_stats[cap]["scores"].append(s_ph)
            post_stats[cap]["success"].append(succ_ph)
            post_stats[cap]["times"].append(t_ph)
            post_stats[cap]["examined"].append(examined)
            post_stats[cap]["batches"].append(batches)

    print("\n" + "=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)

    print(
        f"UNCONSTRAINED | valid@5={mean(uncon_valids):.4f} | "
        f"success@5={mean(uncon_success):.4f} | "
        f"score={mean(uncon_scores):.4f} | "
        f"avg_time={uncon_time / len(TESTS):.4f}"
    )

    print(
        f"PRE-HOC       | valid@5={mean(pre_valids):.4f} | "
        f"success@5={mean(pre_success):.4f} | "
        f"score={mean(pre_scores):.4f} | "
        f"avg_time={pre_time / len(TESTS):.4f}"
    )

    print("\nPOST-HOC SWEEP")
    for cap in POSTHOC_CAPS:
        vals = post_stats[cap]["valids"]
        scores = post_stats[cap]["scores"]
        success = post_stats[cap]["success"]
        times = post_stats[cap]["times"]
        examined = post_stats[cap]["examined"]
        batches = post_stats[cap]["batches"]

        print(
            f"POST-HOC cap={cap:<3} | "
            f"valid@5={mean(vals):.4f} | "
            f"success@5={mean(success):.4f} | "
            f"score={mean(scores):.4f} | "
            f"avg_time={mean(times):.4f} | "
            f"avg_examined={mean(examined):.2f} | "
            f"avg_batches={mean(batches):.2f}"
        )


if __name__ == "__main__":
    main()
