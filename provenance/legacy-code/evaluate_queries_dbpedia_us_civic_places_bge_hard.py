import evaluate_queries_dbpedia_us_civic_places_bge as evaluator
from benchmark_queries_dbpedia_us_civic_places_hard import TESTS


if __name__ == "__main__":
    evaluator.TESTS = TESTS
    evaluator.main()
