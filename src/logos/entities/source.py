"""
Data source entity.

"""

from enum import StrEnum
from pathlib import Path
from typing import Self

from pydantic import BaseModel


class SourceType(StrEnum):
    """
    Source type enumeration.
    """

    article = "article"
    book = "book"
    conference = "conference"
    lecture = "lecture"
    letter = "letter"
    other = "other"
    words = "words"


class Source(BaseModel):
    """
    Data source entity.
    """

    title: str
    type: SourceType
    path: str

    @classmethod
    def from_path(cls, path: str) -> Self:
        """
        Create a Source from a path.
        """
        type_str = Path(path).parent.name.lower()
        return cls(
            title=Path(path).stem,
            type=SourceType(type_str.rstrip("s") if type_str != "words" else type_str),
            path=path,
        )

    def load(self) -> str:
        """
        Load the source file as text.
        """
        return Path(self.path).read_text(encoding="utf-8")

    def __str__(self) -> str:
        return f"{self.type.title()} {self.title!r}"
