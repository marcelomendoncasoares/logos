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

from logos.app.components.button import back_to_top, copy_to_clipboard_button
from logos.app.components.container import custom_css_container
from logos.app.components.empty import add_vertical_space
from logos.app.components.paginate import Paginate
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
        score = f"Score: **:orange[{result.score:.4f}]**"
        metadata, text = result.text.embed_text.split("\n\n", 1)

        # TODO: Improve the paragraph representation parsing.
        try:
            source, headers = (
                metadata.split("\n") if "\n" in metadata else (metadata, "")
            )
            headers = "]\n  - :green[".join(headers.split(": ", 1)[1].split(">>>"))
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
            f"{paragraph_repr.strip()}".replace("...", ":orange[...]")
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
                        # TODO: Fix background flashing black on reload (Chrome).
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

    back_to_top(key="main_back_to_top_button")
