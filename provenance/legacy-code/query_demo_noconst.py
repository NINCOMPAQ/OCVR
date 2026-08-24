from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

COLLECTION = "atmonto_minilm"

def main():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = QdrantClient(url="http://localhost:6333")

    query = "navigation waypoint near JFK"

    print("Query:", query)

    qvec = model.encode([query], normalize_embeddings=True)[0].tolist()

    hits = client.query_points(
        collection_name=COLLECTION,
        query=qvec,
        limit=5,
        with_payload=True
    ).points

    for i, hit in enumerate(hits, 1):
        p = hit.payload
        print(f"\nResult {i}")
        print("Score:", hit.score)
        print("Label:", p.get("label"))
        print("IRI:", p.get("iri"))
        print("Types:", p.get("types"))

if __name__ == "__main__":
    main()