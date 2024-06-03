"""
Pagination components.

"""

from typing import Generic, Sequence, TypeVar

import streamlit as st

from streamlit.delta_generator import DeltaGenerator
from streamlit_utils.state import session_state

from logos.app.components.container import custom_css_container


T = TypeVar("T")


@session_state
class PaginationState:
    """
    State for pagination.

    TODO: Make this able to be instantiated with a key.
    """

    page_size: int = 25


class Paginate(Generic[T]):
    """
    Transforms a list of data into pages.

    """

    def __init__(
        self,
        data: list[T],
        key: str | None = None,
        *,
        page_size_options: Sequence[int] = (10, 25, 50, 100),
    ) -> None:
        """
        Initialize the pagination.

        Args:
            data: Collection of data to paginate (must implement len and slice).
            key: Key to use for the pagination state.
            page_size_options: Options for the page size selector.
        """
        self.data = data
        self.key = key
        self.page_size = PaginationState.page_size
        self.page_size_options = page_size_options
        self.total_pages = (len(data) + self.page_size - 1) // self.page_size

    def get_page(self, page_number: int) -> list[T]:
        """
        Get a page of data by its number.
        """
        start = (page_number - 1) * self.page_size
        end = start + self.page_size
        return self.data[start:end]

    def incremental(
        self,
        col_page_info: DeltaGenerator,
        col_page_indicator: DeltaGenerator,
        col_page_size_select: DeltaGenerator,
    ) -> int:
        """
        Pagination indicator with incremental buttons and a page size selector.

        Args:
            col_page_info: Column to display the page info.
            col_page_indicator: Column to display the page indicator with buttons.
            col_page_size_select: Column to display the page size selector.

        Returns:
            The current page number.
        """
        with col_page_size_select:
            self.page_size = st.selectbox(
                "Page Size",
                options=self.page_size_options,
                key="PaginationState.page_size",
                label_visibility="collapsed",
            )

        with col_page_indicator:
            current_page = st.number_input(
                "Page",
                min_value=1,
                max_value=self.total_pages,
                step=1,
                key=f"{self.key}_page_number" if self.key else None,
                label_visibility="collapsed",
            )

        with col_page_info, custom_css_container("pg_info", "{margin-top: 7px;}"):
            st.markdown(f"Page **{current_page}** of **{self.total_pages}**")

        return current_page
