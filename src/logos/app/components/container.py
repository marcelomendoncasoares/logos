"""
Custom Streamlit container that can have the style customized using CSS.

"""

from typing import TYPE_CHECKING

import streamlit as st


if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator


def custom_css_container(key: str, css_styles: str | list[str]) -> "DeltaGenerator":
    """
    Insert a container into your app which you can style using CSS.
    This is useful to style specific elements in your app.

    Args:
        key: The key associated with this container. Need to be unique since
            all styles will be applied to the container with this key.
        css_styles: The CSS styles to apply to the container elements. Can be
            either a single CSS block or a list of CSS blocks.

    Returns:
        A container object. Elements can be added to this container using
        either the 'with' notation or by calling methods directly on the
        returned object.
    """

    if isinstance(css_styles, str):
        css_styles = [css_styles]

    css_styles.append("\n> div:first-child {\n    margin-bottom: -1rem;\n}\n")
    style_text = "\n<style>\n"
    for style in css_styles:
        style_text += (
            f"\n\n"
            f'div[data-testid="stVerticalBlock"]:has(> div.element-container > '
            f'div.stMarkdown > div[data-testid="stMarkdownContainer"] > '
            f"p > span.{key}) {style}"
            f"\n\n"
        )
    style_text += f'\n    </style>\n\n<span class="{key}"></span>\n'

    container = st.container()
    container.markdown(style_text, unsafe_allow_html=True)
    return container
