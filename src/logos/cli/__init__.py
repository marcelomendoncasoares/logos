"""
Logos CLI entrypoint.

"""

from fnmatch import fnmatch
from pathlib import Path
from typing import Optional
from warnings import simplefilter

import typer

from logos.config import Config
from logos.data.extract import (
    load_documents,
    parse_documents_into_nodes,
    parse_nodes_into_text_chunks,
)
from logos.data.index import delete_index, get_or_create_index, index_documents
from logos.search.index import search_index


simplefilter("ignore", category=FutureWarning)

app = typer.Typer(no_args_is_help=True)
"""Main CLI app to group commands."""


@app.command()
def index(  # noqa: PLR0913
    paths: list[Path],
    *,
    include: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
    limit: int = 0,
    reset: bool = False,
    model: Optional[str] = None,
    fast: bool = False,
) -> None:
    """
    Index all files in the provided paths.

    Directories will be recursively searched. The include clause is evaluated
    first, selecting only matching files. Both include and exclude clauses
    accept glob patterns.

    Note: If the index already exists, it will be updated with the new data.
    Passing `model` or `fast` will reset the index.

    Args:
        paths: List of paths to load documents from.
        include: List of glob pattern to match files to keep (evaluated first).
        exclude: List of glob pattern to match files to exclude.
        limit: Maximum number of nodes to index. If 0, all nodes are indexed.
        reset: Whether to reset the index before indexing.
        model: Custom HuggingFace sentence-transformers model to use for indexing.
        fast: Whether to use a small model to speed up indexing. Ideal for testing.
    """
    if not paths:
        typer.echo("No paths provided.")
        raise typer.Exit(code=1)

    paths = [
        rp
        for p in paths
        for rp in (list(p.rglob("*")) if p.is_dir() else [p])
        if rp.is_file()
    ]

    if include:
        paths = [p for p in paths if any(fnmatch(str(p), i) for i in include)]
    if exclude:
        paths = [p for p in paths if not any(fnmatch(str(p), e) for e in exclude)]

    if reset or fast or model:
        delete_index()
    if fast or model:
        Config.MODEL_PATH = model or "intfloat/multilingual-e5-small"
        get_or_create_index.cache_clear()

    documents = load_documents(input_files=paths)
    nodes = parse_documents_into_nodes(documents)
    text_chunks = parse_nodes_into_text_chunks(nodes)
    index_documents(text_chunks if not limit else text_chunks[:limit])


@app.command()
def delete(*, yes: bool = False) -> None:
    """
    Delete the index.
    """
    if not (yes or typer.confirm("Are you sure to delete the index?", abort=True)):
        return
    delete_index()


@app.command()
def search(query: str, min_score: float = 0.0, limit: Optional[int] = None) -> None:
    """
    Search for text in the index.

    Args:
        query: Text to search for.
        min_score: Minimum score to consider.
        limit: Maximum number of results to return.
    """
    typer.echo(f"\nResults for query: '{query}'\n")
    for result in search_index(query, min_score=min_score, limit=limit):
        typer.echo("------------------------")
        typer.echo(f"Score: {result.score:.4f}\n{result.text.embed_text}\n")


if __name__ == "__main__":
    app()
