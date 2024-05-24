"""
Document extraction process.

"""

from pathlib import Path
from typing import Any
from uuid import NAMESPACE_DNS, uuid5

from llama_index import SimpleDirectoryReader
from llama_index.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.schema import (
    BaseNode,
    Document,
    MetadataMode,
    NodeRelationship,
    TextNode,
)

from logos.entities.paragraph import ParagraphReference
from logos.entities.source import Source
from logos.entities.text import TextChunk


def load_documents(
    input_dir: str | Path | None = None,
    input_files: list[str] | list[Path] | None = None,
) -> list[Document]:
    """
    Load input documents or recursively from a directory.
    Either `input_dir` or `input_files` must be provided.

    Args:
        input_dir: Path to the directory to load documents recursively.
        input_files: List of files to include. If None, include all files.

    Returns:
        List of extracted documents.
    """
    reader = SimpleDirectoryReader(
        input_dir=input_dir,
        input_files=input_files,
        recursive=True,
        file_metadata=lambda path: {"source": Source.from_path(path)},
    )
    documents = reader.load_data(show_progress=True)
    for doc in documents:
        doc.excluded_embed_metadata_keys = ["paragraphs"]
        doc.excluded_llm_metadata_keys = ["paragraphs"]
    return documents


class _CustomMarkdownNodeParser(MarkdownNodeParser):
    """
    Markdown node parser that removes headers from the text.
    Will also remove 'NULL' headers.
    """

    def _build_node_from_split(
        self,
        text_split: str,
        node: BaseNode,
        metadata: dict[str, Any],
    ) -> TextNode:
        headers = []
        for key, header in sorted(metadata.items()):
            if not key.lower().startswith("header"):
                continue
            text_split = text_split.replace(header, "").strip("#").strip()
            current_header = metadata.pop(key)
            if current_header != "NULL":
                headers.append(current_header)

        if headers:
            metadata["headers"] = headers
        metadata["paragraphs"] = ParagraphReference.extract_all(text_split)
        return super()._build_node_from_split(text_split, node, metadata)


def _post_process_nodes_fix_node(nodes: list[TextNode]) -> None:
    """
    Change nodes ID by deterministic UUID5 and update paragraphs metadata.
    """
    for node in nodes:
        node.id_ = str(uuid5(NAMESPACE_DNS, node.get_content(MetadataMode.ALL)))
        node.metadata["paragraphs"] = ParagraphReference.extract_all(node.get_content())


def _post_process_nodes_fix_relationships(nodes: list[TextNode]) -> None:
    """
    Fix relationships between nodes after IDs changes.
    """
    for node, next_node in zip(nodes[:-1], nodes[1:]):
        if node.metadata["source"] != next_node.metadata["source"]:
            node.relationships.pop(NodeRelationship.NEXT)
            next_node.relationships.pop(NodeRelationship.PREVIOUS)
            continue

        node.relationships[NodeRelationship.NEXT] = next_node.as_related_node_info()
        next_node.relationships[NodeRelationship.PREVIOUS] = node.as_related_node_info()
        if not next_node.metadata.get("paragraphs"):
            next_node.metadata["paragraphs"] = node.metadata["paragraphs"]


def parse_documents_into_nodes(documents: list[Document]) -> list[TextNode]:
    """
    Parse documents into text nodes.
    """

    markdown_parser = _CustomMarkdownNodeParser.from_defaults()
    section_nodes = markdown_parser.get_nodes_from_documents(documents)

    sentence_parser = SentenceSplitter.from_defaults(
        chunk_size=192,
        chunk_overlap=32,
        paragraph_separator="\n\n",
    )
    nodes = sentence_parser.get_nodes_from_documents(section_nodes)
    _post_process_nodes_fix_node(nodes)
    _post_process_nodes_fix_relationships(nodes)

    # Assert all nodes have paragraphs
    no_ref = [node for node in nodes if len(node.metadata.get("paragraphs", [])) == 0]
    if len(no_ref) > 0:
        raise ValueError(f"There are {len(no_ref)} nodes without paragraphs: {no_ref}")

    return nodes


def parse_nodes_into_text_chunks(nodes: list[TextNode]) -> list[TextChunk]:
    """
    Parse text nodes into text chunks.
    """
    return [TextChunk.from_text_node(node) for node in nodes]
