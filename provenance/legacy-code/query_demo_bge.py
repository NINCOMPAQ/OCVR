from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny


COLLECTION = "atmonto_bge_large_en_v1_5"

def main():
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    client = QdrantClient(url="http://localhost:6333")

    query = "navigation waypoint near JFK"
    #constraint = "https://data.nasa.gov/ontologies/atmonto/NAS#InternationalAirport"

    qvec = model.encode([query], normalize_embeddings=True)[0].tolist()

    query_filter = Filter(
        must=[
            FieldCondition(
                key="types_closure",
                match=MatchAny(any=[
                    "https://data.nasa.gov/ontologies/atmonto/ATM#IntersectionFix",
                    "https://data.nasa.gov/ontologies/atmonto/ATM#LatLonFix"
                ])
            )
        ]
    )

    hits = client.query_points(
        collection_name=COLLECTION,
        query=qvec,
        query_filter=query_filter,
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
