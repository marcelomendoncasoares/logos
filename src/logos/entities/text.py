"""
Text entity.

"""

from typing import Any, Self

from llama_index.schema import TextNode
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
    prev_id: str | None = None
    next_id: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """
        Post-init hook for the model.
        """
        if self.text.startswith("Source: "):
            self.text = self.text.split("\n\n", 1)[-1]

    @classmethod
    def from_text_node(cls, node: TextNode) -> Self:
        """
        Create a TextChunk from a LLama-Index TextNode.
        """
        return cls(
            id=node.id_,
            text=node.text,
            source=node.metadata["source"],
            headers=node.metadata.get("headers", []),
            paragraphs=node.metadata["paragraphs"],
            prev_id=node.prev_node.node_id if node.prev_node else None,
            next_id=node.next_node.node_id if node.next_node else None,
        )

    @classmethod
    def from_text_nodes(cls, nodes: list[TextNode]) -> list[Self]:
        """
        Create TextChunks from a list of LLama-Index TextNodes.
        """
        return [cls.from_text_node(node) for node in nodes]

    def to_simple_text_node(self) -> TextNode:
        """
        Convert the TextChunk to a simple TextNode.
        """
        return TextNode(
            id_=self.id,
            text=self.embed_text,
            metadata={
                "source": self.source,
                "headers": self.headers,
                "paragraphs": self.paragraphs,
            },
        )

    @property
    def embed_text(self) -> str:
        """
        Text representation prepared for embedding.
        """
        quoted_headers = [f"{h!r}" for h in self.headers]
        headers = f"Headers: {' >>> '.join(quoted_headers)}\n" if self.headers else ""
        return f"Source: {self.source}\n{headers}\n{self.text}"
