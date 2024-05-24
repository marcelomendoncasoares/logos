"""
Query results entity.

"""

from pydantic import BaseModel

from logos.entities.text import TextChunk


class QueryResult(BaseModel):
    """
    Query result entity.
    """

    text: TextChunk
    score: float
    # TODO: Add explainability
