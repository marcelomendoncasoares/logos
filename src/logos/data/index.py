"""
Indexing functions for the CLI.

"""

import shutil

from pathlib import Path

from tqdm import tqdm
from txtai.embeddings import Embeddings

from logos.entities.text import TextChunk


INDEX_DEFAULT_LOCATION = Path.home() / ".logos" / "index"
"""Path to the default location of the index."""


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
    embeddings = get_or_create_index()
    embeddings.upsert(
        tqdm(
            iterable=[(doc.id, doc.model_dump(exclude="id")) for doc in data],
            desc="Indexing text chunks",
            unit="chunk",
        ),
    )
    embeddings.save(str(INDEX_DEFAULT_LOCATION))


def delete_index() -> None:
    """
    Delete the index.
    """
    shutil.rmtree(INDEX_DEFAULT_LOCATION, ignore_errors=True)
