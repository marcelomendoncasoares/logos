"""
ParagraphReference entity.

"""

import re

from typing import Self

from pydantic import BaseModel


REFERENCE_REGEX = (
    r"\[((?P<page_type>pag|solapas|tapa) (?P<page_num>\d+) )?par (?P<paragraph>\d+)\] "
)
"""Regex pattern to match paragraph references."""


class ParagraphReference(BaseModel):
    """
    Paragraph reference entity.
    """

    paragraph: int
    page_num: int | None = None
    page_type: str | None = None

    @classmethod
    def extract_all(cls, text: str, *, remove: bool = False) -> list[Self]:
        """
        Extract all paragraph references from a text.

        Args:
            text: Text to extract references from.
            remove: Whether to remove references from the text during extraction.

        Returns:
            List of found references.
        """
        found_refs = [
            cls(**match.groupdict()) for match in re.finditer(REFERENCE_REGEX, text)
        ]
        if remove:
            text = re.sub(REFERENCE_REGEX, "", text)
        return found_refs

    def __str__(self) -> str:
        if self.page_num is None:
            return f"par {self.paragraph}"
        return f"{self.page_type or 'pag'} {self.page_num} par {self.paragraph}"
