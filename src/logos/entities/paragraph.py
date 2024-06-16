"""
ParagraphReference entity.

"""

import re

from typing import Self

from pydantic import BaseModel


REFERENCE_REGEX = (
    r"(\[|\()"
    r"((?P<page_type>pag|pág\.|solapas|tapa) (?P<page_num>\d+) )?"
    r"(par|§) (?P<paragraph>\d+)"
    r"(\]|\)) "
)
"""
Regex pattern to match paragraph references.

The pattern can be described as follows:
    - Reference can be surrounded by square brackets or parentheses.
    - Page number is optional and preceded by a page type if present.
    - Page type can be one of "pag", "pág.", "solapas" or "tapa".
    - When present, the page number comes before the paragraph number.
    - Paragraph number is always present and preceded by "par" or "§".
    - All elements are separated by spaces.
    - The closing bracket/parentheses is always followed by a space.
"""


class ParagraphReference(BaseModel):
    """
    Paragraph reference entity.
    """

    paragraph: int
    page_num: int | None = None
    page_type: str | None = None

    @classmethod
    def extract_all(cls, text: str) -> list[Self]:
        """
        Extract a list of all paragraph references found in a text.
        """
        return [cls(**m.groupdict()) for m in re.finditer(REFERENCE_REGEX, text)]

    @classmethod
    def remove(cls, text: str) -> str:
        """
        Remove all paragraph references from a text.
        """
        return re.sub(REFERENCE_REGEX, lambda _: "", text)

    @classmethod
    def format(cls, text: str) -> str:
        """
        Format all paragraph references in a text in a more user-readable format.
        """
        return re.sub(REFERENCE_REGEX, lambda m: f"({cls(**m.groupdict())}) ", text)

    @classmethod
    def startswith(cls, text: str) -> bool:
        """
        Whether a text starts with a paragraph reference.
        """
        return re.match(REFERENCE_REGEX, text) is not None

    @classmethod
    def split(cls, text: str) -> list[str]:
        """
        Split a text into all paragraphs that start with a paragraph reference.
        """
        result = [text]
        for m in re.finditer(REFERENCE_REGEX, result[-1]):
            split_pos = m.start() - 1
            if split_pos == 0:
                continue
            result.append(result[-1][split_pos:].strip())
            result[-2] = result[-2][:split_pos].strip()
        return result

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        if self.page_num is None:
            return f"§ {self.paragraph}"
        page_type = self.page_type or "pág."
        if self.page_type == "pag":
            page_type = "pág."
        return f"{page_type} {self.page_num} § {self.paragraph}"
