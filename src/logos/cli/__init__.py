"""
Logos CLI entrypoint.

"""

from fnmatch import fnmatch
from pathlib import Path
from typing import Optional
from warnings import simplefilter

import typer

from rich import print


simplefilter("ignore", category=FutureWarning)

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
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
    print("\n[bold]Initializing...[/bold]")

    from logos.config import Config
    from logos.data.extract import (
        load_documents,
        parse_documents_into_nodes,
        parse_nodes_into_text_chunks,
    )
    from logos.data.index import delete_index, get_or_create_index, index_documents

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

    if fast or model:
        Config.MODEL_PATH = model or "intfloat/multilingual-e5-small"
        model_url = f"https://huggingface.co/{Config.MODEL_PATH}"
        model_print = f"[link={model_url}]{Config.MODEL_PATH}[/link]"
        print(f"Using model: [bold yellow]{model_print}[/bold yellow].\n")
        get_or_create_index.cache_clear()
    if reset or fast or model:
        print("Deleting existing index...")
        delete_index()

    print("Starting index process...")
    documents = load_documents(input_files=paths)
    nodes = parse_documents_into_nodes(documents)
    text_chunks = parse_nodes_into_text_chunks(nodes)
    index_documents(text_chunks if not limit else text_chunks[:limit])
    print("[bold green]All nodes indexed with success.\n")


@app.command()
def delete(*, yes: bool = False) -> None:
    """
    Delete the index.
    """
    if not (yes or typer.confirm("Are you sure to delete the index?", abort=True)):
        return
    print("[red]Deleting[/red] existing index...")

    from logos.data.index import delete_index

    delete_index()
    print("[bold green]Index deleted with success.\n")


@app.command()
def search(query: str, min_score: float = 0.0, limit: Optional[int] = None) -> None:
    """
    Search for text in the index.

    Args:
        query: Text to search for.
        min_score: Minimum score to consider.
        limit: Maximum number of results to return.
    """
    print("\n[bold]Initializing...[/bold]")

    from logos.entities.paragraph import ParagraphReference
    from logos.search.index import search_index

    print(f"\nResults for query: [yellow]'{query}'\n")
    for result in search_index(query, min_score=min_score, limit=limit):
        print(f"[gray]{'-'*80}")
        print(f"Score: [yellow]{result.score:.4f}")
        metadata, text = result.text.embed_text.split("\n\n", 1)
        metadata += f"\nParagraphs: {', '.join(map(str, result.text.paragraphs))}"
        print(f"{metadata}\n\n[italic]{ParagraphReference.format(text)}[/italic]\n")


if __name__ == "__main__":
    app()
