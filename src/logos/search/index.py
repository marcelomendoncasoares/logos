"""
Search functions for the index.

"""

import json

from typing import Type, TypeVar

from logos.data.index import get_or_create_index
from logos.entities.query import QueryResult
from logos.entities.text import TextChunk


ReturnType = TypeVar("ReturnType", bound=QueryResult | TextChunk)


def _convert_result(data: dict, cls: Type[ReturnType]) -> ReturnType:
    """
    Convert a result of an Embedding query to a QueryResult.
    """
    data["text"] = json.loads(data.pop("data"))
    data["text"]["id"] = data.pop("id")
    if cls is TextChunk:
        data = data["text"]
    return cls(**data)


def search_index(
    similarity_query: str,
    min_score: float = 0.0,
    limit: int | None = None,
) -> list[QueryResult]:
    """
    Search the index with a query.

    Args:
        similarity_query: Similarity query to search for.
        min_score: Minimum score to consider.
        limit: Maximum number of results to return.

    Returns:
        List of text chunks.
    """
    results: list[dict] = get_or_create_index().search(
        query="""
            select id, data, score
            from txtai
            where similar(:query) and score > :min_score
        """,
        limit=limit,
        parameters={"query": similarity_query, "min_score": min_score},
    )
    return [_convert_result(data, QueryResult) for data in results]


def get_items_by_id(*ids: str) -> list[TextChunk]:
    """
    Get items by their IDs.
    """
    items: list[dict] = get_or_create_index().search(
        query="""
            select id, data
            from txtai
            where id in (:ids_list)
        """,
        parameters={"ids_list": f"""'{"','".join(ids)}'"""},
    )
    return [_convert_result(data, TextChunk) for data in items]
