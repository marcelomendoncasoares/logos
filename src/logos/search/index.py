"""
Search functions for the index.

"""

from logos.data.index import get_or_create_index
from logos.entities.query import QueryResult
from logos.entities.text import TextChunk
from logos.search.rerank import rerank_results


def search_index(
    query: str,
    *,
    rerank: bool = True,
    limit: int | None = None,
) -> list[QueryResult]:
    """
    Search the index with a query.

    Args:
        query: Similarity query to search for.
        rerank: Whether to rerank the results.
        limit: Maximum number of results to return.

    Returns:
        List of text chunks.
    """
    retriever = get_or_create_index().as_retriever(
        similarity_top_k=limit,
        alpha=0.5,  # NOTE: only for hybrid search (0 for bm25, 1 for vector search)
    )
    query_results = [
        QueryResult(text=TextChunk.from_text_node(r.node), score=r.score)
        for r in retriever.retrieve(query)
    ]
    if rerank:
        return rerank_results(query=query, results=query_results)
    return query_results
