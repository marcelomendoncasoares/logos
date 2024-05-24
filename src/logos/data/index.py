"""
Indexing functions for the CLI.

"""

import json
import shutil

from functools import lru_cache
from pathlib import Path
from typing import Type, TypeVar

from tqdm import tqdm
from txtai.embeddings import Embeddings

from logos.entities.query import QueryResult
from logos.entities.text import TextChunk


ReturnType = TypeVar("ReturnType", bound=QueryResult | TextChunk)


INDEX_DEFAULT_LOCATION = Path.home() / ".logos" / "index"
"""Path to the default location of the index."""


@lru_cache
def get_or_create_index() -> Embeddings:
    """
    Get or create the index.
    """

    if not INDEX_DEFAULT_LOCATION.exists() or (
        INDEX_DEFAULT_LOCATION.is_dir() and not list(INDEX_DEFAULT_LOCATION.glob("*"))
    ):
        return Embeddings(
            autoid="uuid5",
            keyword=True,
            hybrid=True,
            path="intfloat/multilingual-e5-large",
            instructions=dict(
                query="query: ",
                data="passage: ",
            ),
            content=True,
            scoring=dict(
                method="bm25",
                terms=True,
                normalize=True,
            ),
        )

    embeddings = Embeddings()
    embeddings.load(str(INDEX_DEFAULT_LOCATION))
    return embeddings


def index_documents(data: list[TextChunk]) -> None:
    """
    Index a list of documents.
    """

    # Replace the text with the representation prepared for embedding
    for doc in data:
        doc.text = doc.embed_text

    embeddings = get_or_create_index()
    embeddings.upsert(
        tqdm(
            iterable=[(doc.id, doc.model_dump(exclude="id")) for doc in data],
            desc="Indexing text chunks",
            unit="chunk",
        ),
    )
    embeddings.save(str(INDEX_DEFAULT_LOCATION))


def _convert_result(data: dict, cls: Type[ReturnType]) -> ReturnType:
    """
    Convert a result of an Embedding query to a QueryResult.
    """
    data["text"] = json.loads(data.pop("data"))
    data["text"]["id"] = data.pop("id")
    if cls is TextChunk:
        data = data["text"]
    return cls(**data)


def search_index(similarity_query: str, limit: int | None = None) -> list[QueryResult]:
    """
    Search the index with a query.

    Args:
        similarity_query: Similarity query to search for.
        limit: Maximum number of results to return.

    Returns:
        List of text chunks.
    """
    results: list[dict] = get_or_create_index().search(
        query="""
            select id, data, score
            from txtai
            where similar(:query)
        """,
        limit=limit,
        parameters={"query": similarity_query},
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


def delete_index() -> None:
    """
    Delete the index.
    """
    shutil.rmtree(INDEX_DEFAULT_LOCATION, ignore_errors=True)
