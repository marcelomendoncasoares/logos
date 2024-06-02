"""
Empty space components.

"""

import streamlit as st


def add_vertical_space(num_lines: int = 1) -> None:
    """
    Add vertical space to the Streamlit app.

    Args:
        num_lines: Height of the vertical space (given in number of lines).
    """
    for _ in range(num_lines):
        st.write("")
