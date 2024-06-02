"""
Logos search web application.

"""

import re

from typing import TYPE_CHECKING

import streamlit as st

from st_keyup import st_keyup
from streamlit_float import float_init, float_parent
from streamlit_pills import pills
from streamlit_utils.state import session_state

from logos.app.components.button import copy_to_clipboard_button
from logos.app.components.container import custom_css_container
from logos.app.components.empty import add_vertical_space
from logos.app.components.theme import get_theme
from logos.entities.paragraph import ParagraphReference


if TYPE_CHECKING:
    from logos.entities.query import QueryResult


@session_state
class LogosState:
    """
    Session state for the main page of the Logos application.
    """

    counter: int = 0
    query: str = ""
    previous_query: str = ""


st.set_page_config(
    page_title="Logos Search",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto",
)


@st.cache_data
def execute_search(query: str) -> list["QueryResult"]:
    """
    Execute a search query.
    """
    from logos.search.index import search_index

    return search_index(query, limit=100)


float_init()

theme = get_theme()
"""Theme object to be used in the app."""

with custom_css_container(
    key="top_search_bar",
    css_styles=f"""
        {{
            top: 40px;
            background-color: {theme.backgroundColor};
            padding-top: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #9f1117;
            box-shadow: 0 10px 20px -2px {theme.backgroundColor};
        }}
    """,
):
    st_keyup(
        "Logos Search",
        placeholder="What would you like to ask?",
        key="LogosState.query",
        label_visibility="collapsed",
        debounce=500,
    )

    selected = pills(
        label="Label",
        options=["exact", "sparse", "dense"],
        index=None,
        label_visibility="collapsed",
        clearable=True,
    )

    float_parent()

add_vertical_space(4)

# Avoid re-running the code block if the query is the same
if LogosState.query and (LogosState.query != LogosState.previous_query):
    for i, result in enumerate(execute_search(LogosState.query)):
        score = f"Score: **:orange[{result.score:.4f}]**"
        metadata, text = result.text.embed_text.split("\n\n", 1)

        # TODO: Improve the paragraph representation parsing.
        try:
            source, headers = (
                metadata.split("\n") if "\n" in metadata else (metadata, "")
            )
            headers = "]\n  - :green[".join(headers.split(": ")[1].split(">>>"))
            paragraphs = f"Paragraphs: {', '.join(map(str, result.text.paragraphs))}"
            paragraphs = re.sub(r"\b\d+\b", ":blue[\\g<0>]", paragraphs)
            metadata_repr = f"- {source}\n  - :green[{headers}]\n- {paragraphs}"
        except:  # noqa: E722, S112
            continue

        paragraph_reprs = [
            re.sub(r"\b\d+\b", ":blue[\\g<0>]", paragraph)
            for paragraph in ParagraphReference.format(text).split("\n\n")
        ]
        paragraph_reprs = [
            f"_{paragraph_repr.strip()}_".replace("...", ":orange[...]")
            for paragraph_repr in paragraph_reprs
        ]

        with st.container(border=True):
            st.markdown(score)
            st.markdown(metadata_repr)
            for j, paragraph_repr in enumerate(paragraph_reprs):
                with custom_css_container(
                    key="teaching_container",
                    css_styles=f"""
                        {{
                            background-color: {theme.bgMix};
                            border-radius: 7px;
                            padding: 20px;
                        }}
                        button:hover {{
                            color: {theme.textColor} !important;
                            opacity: 1 !important;
                            transition: .3s;
                        }}
                    """,
                ):
                    main_col, copy_button_col = st.columns([1.0, 0.07])
                    with main_col:
                        st.markdown(paragraph_repr)

                    with copy_button_col, custom_css_container(
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
                    ):
                        # TODO: Improve the text to be copied.
                        # TODO: Add a toast message when the text has been copied.
                        # TODO: Add a helper tooltip to the button when hovered.
                        copy_to_clipboard_button(
                            paragraph_repr,
                            key=f"copy_button_{i}_{j}",
                        )
                        st.button(
                            label="⛶",  # "↕",
                            key=f"expand_button_{i}_{j}",
                            help="Expand surrounding context",
                            on_click=st.toast,
                            args=("Context expansion is not implemented yet.",),
                            use_container_width=True,
                        )
