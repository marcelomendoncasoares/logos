"""
Logos search web application.

"""

import re

from typing import TYPE_CHECKING

import streamlit as st

from streamlit_float import float_init, float_parent
from streamlit_pills import pills
from streamlit_utils.state import session_state

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
    st.text_input(
        "Logos Search",
        placeholder="What would you like to ask?",
        key="LogosState.query",
        label_visibility="collapsed",
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
if LogosState.query != LogosState.previous_query:
    for result in execute_search(LogosState.query):
        st.divider()
        st.markdown(f"Score: **:orange[{result.score:.4f}]**")
        metadata, text = result.text.embed_text.split("\n\n", 1)
        source, headers = metadata.split("\n")
        headers = "]\n  - :green[".join(headers.split(": ")[1].split(">>>"))
        paragraphs = f"Paragraphs: {', '.join(map(str, result.text.paragraphs))}"
        paragraphs = re.sub(r"\b\d+\b", ":blue[\\g<0>]", paragraphs)
        metadata = f"- {source}\n  - :green[{headers}]\n- {paragraphs}"
        st.markdown(metadata)
        for paragraph in ParagraphReference.format(text).split("\n\n"):
            paragraph_repr = re.sub(r"\b\d+\b", ":blue[\\g<0>]", paragraph)
            st.markdown(f"_{paragraph_repr.strip()}_".replace("...", ":orange[...]"))
