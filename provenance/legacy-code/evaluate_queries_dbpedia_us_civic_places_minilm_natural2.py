import evaluate_queries_dbpedia_us_civic_places_bge as evaluator
from benchmark_queries_dbpedia_us_civic_places_natural2 import TESTS


if __name__ == "__main__":
    original = evaluator.SentenceTransformer
    evaluator.SentenceTransformer = lambda _name: original("sentence-transformers/all-MiniLM-L6-v2")
    evaluator.COLLECTION = "dbpedia_us_civic_places_minilm_enriched"
    evaluator.TESTS = TESTS
    evaluator.main()
