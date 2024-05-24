"""
Text entity.

"""

from typing import Self

from llama_index.schema import MetadataMode, TextNode
from pydantic import BaseModel

from logos.entities.paragraph import ParagraphReference
from logos.entities.source import Source


class TextChunk(BaseModel):
    """
    Text chunk model.
    """

    id: str
    text: str
    source: Source
    headers: list[str] = []
    paragraphs: list[ParagraphReference]
    # TODO: Add relations: {previous, next}

    @classmethod
    def from_text_node(cls, node: TextNode) -> Self:
        """
        Create a TextChunk from a LLama-Index TextNode.
        """
        return cls(
            id=node.id_,
            text=node.get_content(MetadataMode.EMBED),
            source=node.metadata["source"],
            headers=node.metadata.get("headers", []),
            paragraphs=node.metadata["paragraphs"],
        )
