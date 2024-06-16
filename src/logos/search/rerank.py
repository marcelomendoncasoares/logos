"""
Re-rank functions using `SentenceTransformerRerank`.

"""

from functools import lru_cache

from llama_index.postprocessor import SentenceTransformerRerank

from logos.entities.query import QueryResult


@lru_cache
def get_reranker() -> SentenceTransformerRerank:
    """
    Get the reranker.
    """
    return SentenceTransformerRerank(
        top_n=10,
        model="cross-encoder/ms-marco-MiniLM-L-12-v2",
        keep_retrieval_score=True,
    )


def rerank_results(query: str, results: list[QueryResult]) -> list[QueryResult]:
    """
    Rerank the text chunks.
    """
    nodes = [result.to_simple_node_with_score() for result in results]
    return [
        QueryResult.from_node_with_score(node)
        for node in get_reranker().postprocess_nodes(nodes, query_str=query)
    ]
