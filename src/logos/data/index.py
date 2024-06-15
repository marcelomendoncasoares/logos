"""
Indexing functions for the CLI.

"""

import shutil

from functools import lru_cache
from typing import TYPE_CHECKING

from faiss import IndexFlatL2
from llama_index import (
    ServiceContext,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.schema import TextNode
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores import FaissVectorStore
from tqdm import tqdm

from logos.config import Config
from logos.data.store import SimplePickleKVStore


if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerFast


INDEX_DEFAULT_LOCATION = Config.ROOT_FOLDER / "index_test"
"""Path to the default location of the index."""


@lru_cache
def get_or_create_index() -> VectorStoreIndex:
    """
    Get or create the index.
    """

    if INDEX_DEFAULT_LOCATION.is_dir() and list(INDEX_DEFAULT_LOCATION.glob("*")):
        persist_dir = str(INDEX_DEFAULT_LOCATION)
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        return load_index_from_storage(storage_context)

    embed_model = HuggingFaceEmbedding(
        model_name=Config.MODEL_PATH,
        query_instruction=Config.MODEL_INSTRUCTIONS.query,
        text_instruction=Config.MODEL_INSTRUCTIONS.data,
    )

    embedding_dimension = len(embed_model.get_text_embedding("an example text"))
    faiss_index = IndexFlatL2(embedding_dimension)

    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore(simple_kvstore=SimplePickleKVStore()),
        vector_store=FaissVectorStore(faiss_index),
    )

    service_context = ServiceContext.from_defaults(
        llm=None,
        embed_model=embed_model,
    )

    return VectorStoreIndex.from_documents(
        documents=[],
        service_context=service_context,
        storage_context=storage_context,
        show_progress=True,
    )


def get_embedding_model() -> HuggingFaceEmbedding:
    """
    Get the embedding model used in the index.
    """
    return get_or_create_index().service_context.embed_model


def tokenize_text(text: str) -> list[str]:
    """
    Return the list of tokens for a given text according to the chosen model.
    """
    model = get_embedding_model()
    tokenizer: PreTrainedTokenizerFast = model._tokenizer  # noqa: SLF001
    return tokenizer.tokenize(text)


def index_documents(data: list[TextNode]) -> None:
    """
    Index a list of documents.
    """

    index = get_or_create_index()
    index.insert_nodes(tqdm(iterable=data, desc="Indexing text chunks", unit="chunk"))
    index.storage_context.persist(str(INDEX_DEFAULT_LOCATION))


def delete_index() -> None:
    """
    Delete the index.
    """
    shutil.rmtree(INDEX_DEFAULT_LOCATION, ignore_errors=True)
