"""
Document extraction process.

"""

from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5

from llama_index import SimpleDirectoryReader
from llama_index.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.schema import Document, MetadataMode, NodeRelationship, TextNode

from logos.entities.paragraph import ParagraphReference
from logos.entities.source import Source


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


def _post_process_nodes_hierarchy(nodes: list[TextNode]) -> None:
    """
    Remove headers from the text, remove 'NULL' headers, transform headers
    into a list and extract paragraphs.
    """
    for node in nodes:
        headers = []
        for key, header in sorted(node.metadata.items()):
            if not key.lower().startswith("header"):
                continue
            node.text = node.text.replace(header, "").strip("#").strip()
            current_header = node.metadata.pop(key)
            if current_header != "NULL":
                headers.append(current_header)

        if headers:
            node.metadata["headers"] = headers
        node.metadata["paragraphs"] = ParagraphReference.extract_all(node.text)


def _post_process_nodes_fix_node(nodes: list[TextNode]) -> None:
    """
    Change nodes ID by deterministic UUID5 and update paragraphs metadata.
    """
    for node in nodes:
        node.id_ = str(uuid5(NAMESPACE_DNS, node.get_content(MetadataMode.ALL)))
        node.metadata["paragraphs"] = ParagraphReference.extract_all(node.text)


def _post_process_nodes_remove_empty(nodes: list[TextNode]) -> None:
    """
    Remove nodes that have no content, only headers and paragraph reference.
    """
    for node, next_node in zip(nodes[:-1], nodes[1:]):
        if ParagraphReference.remove(node.text).replace("[...]", "").strip():
            continue
        if node.prev_node:
            next_node.relationships[NodeRelationship.PREVIOUS] = node.prev_node
        else:
            next_node.relationships.pop(NodeRelationship.PREVIOUS)
        nodes.remove(node)


def _post_process_nodes_fix_relationships(nodes: list[TextNode]) -> None:
    """
    Fix relationships between nodes after IDs changes and missing paragraph
    references for text chunks that are in the middle of a paragraph.
    """
    for node, next_node in zip(nodes[:-1], nodes[1:]):
        if node.metadata["source"] != next_node.metadata["source"]:
            node.relationships.pop(NodeRelationship.NEXT)
            next_node.relationships.pop(NodeRelationship.PREVIOUS)
            continue

        next_pars: list[ParagraphReference] = next_node.metadata.get("paragraphs", [])
        if not node.metadata["paragraphs"]:
            raise ValueError(
                f"Neither node {node.node_id} nor its predecessors has paragraphs "
                f"metadata. Its source is {node.metadata['source']} and its text "
                f"is: {node.text}. Its predecessor is {node.prev_node.node_id}.",
            )

        current_last_paragraph = node.metadata["paragraphs"][-1]
        if not next_pars or not ParagraphReference.startswith(next_node.text):
            next_node.metadata["paragraphs"] = [current_last_paragraph, *next_pars]
            next_node.text = f"[{current_last_paragraph}] [...] {next_node.text}"
            node.text = f"{node.text} [...]"

        node.relationships[NodeRelationship.NEXT] = next_node.as_related_node_info()
        next_node.relationships[NodeRelationship.PREVIOUS] = node.as_related_node_info()


def parse_documents_into_nodes(documents: list[Document]) -> list[TextNode]:
    """
    Parse documents into text nodes.
    """
    from logos.data.index import tokenize_text

    markdown_parser = MarkdownNodeParser.from_defaults()
    section_nodes = markdown_parser.get_nodes_from_documents(documents)
    _post_process_nodes_hierarchy(section_nodes)

    sentence_parser = SentenceSplitter.from_defaults(
        chunk_size=192,
        chunk_overlap=32,
        tokenizer=tokenize_text,
        paragraph_separator="\n\n",
    )
    nodes = sentence_parser.get_nodes_from_documents(section_nodes)
    _post_process_nodes_fix_node(nodes)
    _post_process_nodes_remove_empty(nodes)
    _post_process_nodes_fix_relationships(nodes)

    # Assert all nodes have paragraphs
    no_ref = [node for node in nodes if len(node.metadata.get("paragraphs", [])) == 0]
    if len(no_ref) > 0:
        raise ValueError(f"There are {len(no_ref)} nodes without paragraphs: {no_ref}")

    # TODO: Assert that there are N 'ParagraphReferences' equal to the number
    # of paragraphs, which is currently not assured during the extraction.

    return nodes
