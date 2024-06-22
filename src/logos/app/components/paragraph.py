"""
Paragraph component to show a paragraph from a query result.

"""

import re

import streamlit as st

from streamlit.delta_generator import DeltaGenerator

from logos.app.components.button import copy_to_clipboard_button
from logos.app.components.container import custom_css_container
from logos.app.components.theme import ThemeModel
from logos.entities.paragraph import ParagraphReference
from logos.entities.query import QueryResult


class ParagraphComponent:
    """
    Paragraph component to show a paragraph from a query result.
    """

    def __init__(
        self,
        result: QueryResult,
        position: int,
        theme: ThemeModel,
    ) -> None:
        """
        Initialize the paragraph component.

        Args:
            result: Query result to show the paragraph from.
            position: Position of the paragraph in the result.
            theme: Theme to use for the paragraph component.
        """
        self.result = result
        self.theme = theme
        self.position = position

    def _parse_paragraph(self) -> tuple[str, list[str]] | None:
        """
        Parse the paragraph into metadata and paragraph representations.
        """
        metadata, text = self.result.text.embed_text.split("\n\n", 1)

        # TODO: Improve the paragraph representation parsing.
        try:
            source, headers = (
                metadata.split("\n") if "\n" in metadata else (metadata, "")
            )
            headers = "]\n  - :green[".join(headers.split(": ", 1)[1].split(">>>"))
            paragraphs = (
                f"Paragraphs: {', '.join(map(str, self.result.text.paragraphs))}"
            )
            paragraphs = re.sub(r"\b\d+\b", ":blue[\\g<0>]", paragraphs)
            metadata_repr = f"- {source}\n  - :green[{headers}]\n- {paragraphs}"
        except:  # noqa: E722
            return None

        paragraph_reprs = [
            re.sub(r"\b\d+\b", ":blue[\\g<0>]", paragraph)
            for paragraph in ParagraphReference.format(text).split("\n\n")
        ]
        paragraph_reprs = [
            f"{paragraph_repr.strip()}".replace("...", ":orange[...]")
            for paragraph_repr in paragraph_reprs
        ]

        return metadata_repr, paragraph_reprs

    def _teaching_container(self) -> DeltaGenerator:
        return custom_css_container(
            key="teaching_container",
            css_styles=f"""
                {{
                    background-color: {self.theme.bgMix};
                    border-radius: 7px;
                    padding: 20px;
                }}
                button:hover {{
                    color: {self.theme.textColor} !important;
                    opacity: 1 !important;
                    transition: .3s;
                }}
            """,
        )

    def _no_border_button(self) -> DeltaGenerator:
        return custom_css_container(
            key="no_border_button",
            css_styles="""
                button {
                    border: 0px;
                    background-color: transparent;
                    padding: 0px;
                    margin-top: -5px;
                    margin-bottom: -20px;
                    margin-right: -40px;
                    opacity: 0.3;
                    transition: .3s;
                }
            """,
        )

    def _build_side_buttons(self, text_to_copy: str, sub_position: int) -> None:
        # TODO: Add a toast message when the text has been copied.
        # TODO: Add a helper tooltip to the button when hovered.
        # TODO: Fix background flashing black on reload (Chrome).
        copy_to_clipboard_button(
            text_to_copy,
            key=f"copy_button_{self.position}_{sub_position}",
        )
        st.button(
            label="⛶",  # "↕",
            key=f"expand_button_{self.position}_{sub_position}",
            help="Expand surrounding context",
            on_click=st.toast,
            args=("Context expansion is not implemented yet.",),
            use_container_width=True,
        )

    def build(self) -> None:
        """
        Build the paragraph component.
        """
        if not (parsed := self._parse_paragraph()):
            st.warning(f"Failed to parse the paragraph {self.result.text!r}.")
            return
        score = f"Score: **:orange[{self.result.score:.4f}]**"
        metadata_repr, paragraph_reprs = parsed

        with st.container(border=True):
            st.markdown(score)
            st.markdown(metadata_repr)
            for j, paragraph_repr in enumerate(paragraph_reprs):
                with self._teaching_container():
                    main_col, copy_button_col = st.columns([1.0, 0.07])
                    with main_col:
                        st.markdown(paragraph_repr)
                    with copy_button_col, self._no_border_button():
                        # TODO: Improve the text to be copied.
                        self._build_side_buttons(paragraph_repr, j)
