"""
Indexing functions for the CLI.

"""

import shutil

from functools import lru_cache
from typing import TYPE_CHECKING, cast

from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from txtai.embeddings import Embeddings

from logos.config import Config
from logos.entities.text import TextChunk


if TYPE_CHECKING:
    from torch import Tensor
    from transformers import PreTrainedTokenizerFast


INDEX_DEFAULT_LOCATION = Config.ROOT_FOLDER / "index"
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
            method="sentence-transformers",  # Necessary to access the tokenizer
            path=Config.MODEL_PATH,
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


def tokenize_text(text: str) -> list[str]:
    """
    Return the list of tokens for a given text according to the chosen model.
    """
    model = cast(SentenceTransformer, get_or_create_index().model.model)
    tokenizer: PreTrainedTokenizerFast = model.tokenizer
    token_ids: Tensor = model.tokenize([text])["input_ids"][0]
    text_tokens: list[str] = tokenizer.convert_ids_to_tokens(token_ids)
    return text_tokens


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


def delete_index() -> None:
    """
    Delete the index.
    """
    shutil.rmtree(INDEX_DEFAULT_LOCATION, ignore_errors=True)
