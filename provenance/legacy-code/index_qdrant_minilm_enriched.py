import json
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


ENTITIES_PATH = "entities_enriched.jsonl"
COLLECTION = "atmonto_minilm_enriched"
BATCH_SIZE = 128


def iter_entities(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def main():
    print("Loading MiniLM...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    dim = model.get_sentence_embedding_dimension()
    print("Embedding dimension:", dim)

    client = QdrantClient(url="http://localhost:6333")

    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    batch_texts: List[str] = []
    batch_payloads: List[Dict[str, Any]] = []
    batch_ids: List[int] = []

    next_id = 1
    total = 0

    def flush():
        nonlocal total
        if not batch_texts:
            return

        vectors = model.encode(
            batch_texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        points = []
        for i, vec in enumerate(vectors):
            points.append(
                PointStruct(
                    id=batch_ids[i],
                    vector=vec.tolist(),
                    payload=batch_payloads[i],
                )
            )

        client.upsert(collection_name=COLLECTION, points=points)
        total += len(points)
        print(f"Upserted {total} entities...")

        batch_texts.clear()
        batch_payloads.clear()
        batch_ids.clear()

    for ent in iter_entities(ENTITIES_PATH):
        payload = {
            "iri": ent["iri"],
            "label": ent.get("label"),
            "types": ent["types"],
            "types_closure": ent["types_closure"],
        }

        batch_texts.append(ent["card_text"])
        batch_payloads.append(payload)
        batch_ids.append(next_id)
        next_id += 1

        if len(batch_texts) >= BATCH_SIZE:
            flush()

    flush()
    print(f"Done. Indexed {total} entities into '{COLLECTION}'.")


if __name__ == "__main__":
    main()