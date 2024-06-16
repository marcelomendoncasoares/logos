"""
Query results entity.

"""

from llama_index.schema import NodeWithScore
from pydantic import BaseModel

from logos.entities.text import TextChunk


class QueryResult(BaseModel):
    """
    Query result entity.
    """

    text: TextChunk
    score: float | None
    # TODO: Add explainability

    @classmethod
    def from_node_with_score(cls, node: NodeWithScore) -> "QueryResult":
        """
        Create a QueryResult from a LLama-Index NodeWithScore.
        """
        return cls(
            text=TextChunk.from_text_node(node.node),
            score=node.score,
        )

    def to_simple_node_with_score(self) -> NodeWithScore:
        """
        Convert the TextChunk to a simple TextNode.
        """
        return NodeWithScore(
            node=self.text.to_simple_text_node(),
            score=self.score,
        )
