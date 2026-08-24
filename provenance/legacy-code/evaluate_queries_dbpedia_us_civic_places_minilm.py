from evaluate_queries_dbpedia_us_civic_places_bge import main


if __name__ == "__main__":
    import evaluate_queries_dbpedia_us_civic_places_bge as evaluator
    from sentence_transformers import SentenceTransformer

    evaluator.COLLECTION = "dbpedia_us_civic_places_minilm_enriched"

    original = evaluator.SentenceTransformer
    evaluator.SentenceTransformer = lambda _name: original("sentence-transformers/all-MiniLM-L6-v2")
    main()
