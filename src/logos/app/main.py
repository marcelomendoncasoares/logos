"""
Logos search web application.

"""

from typing import TYPE_CHECKING

import streamlit as st

from st_keyup import st_keyup
from streamlit_float import float_init, float_parent
from streamlit_pills import pills
from streamlit_utils.state import session_state

from logos.app.components.button import back_to_top
from logos.app.components.container import custom_css_container
from logos.app.components.empty import add_vertical_space
from logos.app.components.paginate import Paginate
from logos.app.components.paragraph import ParagraphComponent
from logos.app.components.theme import get_theme


if TYPE_CHECKING:
    from logos.entities.query import QueryResult


@session_state
class LogosState:
    """
    Session state for the main page of the Logos application.
    """

    counter: int = 0
    query: str = ""
    current_page: int = 1


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

theme = get_theme(key="main_theme")

with custom_css_container(
    key="top_search_bar",
    css_styles=f"""
        {{
            top: 40px;
            background-color: {theme.backgroundColor};
            padding-top: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid {theme.primaryColor}a0;
            box-shadow: 0 10px 20px -2px {theme.backgroundColor};
        }}
    """,
):
    float_parent()

    st_keyup(
        "Logos Search",
        placeholder="What would you like to ask?",
        key="LogosState.query",
        label_visibility="collapsed",
        debounce=500,
    )

    col_pills, _, col_pages = st.columns((3, 2, 5))

    with col_pills:
        selected = pills(
            label="Label",
            options=["exact", "sparse", "dense"],
            index=None,
            label_visibility="collapsed",
            clearable=True,
        )

    if LogosState.query:
        search_result = execute_search(LogosState.query)
        paginated = Paginate(search_result, key="search_results")
        with col_pages, custom_css_container("pg_container", "{margin-top: -5px;}"):
            LogosState.current_page = paginated.incremental(*st.columns((2, 2.5, 2)))

add_vertical_space(7)

# Avoid re-running the code block if the query is the same
if LogosState.query:
    for i, result in enumerate(paginated.get_page(LogosState.current_page)):
        ParagraphComponent(result, position=i, theme=theme).build()
    back_to_top(key="main_back_to_top_button")
