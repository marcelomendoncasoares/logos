"""
Logos search web application.

"""

import re

from typing import TYPE_CHECKING

import streamlit as st

from streamlit_pills import pills
from streamlit_utils.state import session_state

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
