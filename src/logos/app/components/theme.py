"""
Theme utilities for logos app.
"""

from pydantic import BaseModel
from streamlit_theme import st_theme


# Disable ruff check for camel case attributes due to the attributes of the
# ThemeModel being defined by the Streamlit theme and only used in the app.
# ruff: noqa: N815


class ThemeModel(BaseModel):
    """
    Model that represents the Streamlit theme.
    """

    primaryColor: str
    backgroundColor: str
    secondaryBackgroundColor: str
    textColor: str
    base: str
    font: str
    linkText: str
    fadedText05: str
    fadedText10: str
    fadedText20: str
    fadedText40: str
    fadedText60: str
    bgMix: str
    darkenedBgMix100: str
    darkenedBgMix25: str
    darkenedBgMix15: str
    lightenedBg05: str

    @property
    def is_dark(self) -> bool:
        """
        Check if the theme is dark.
        """
        return self.base.lower() == "dark"

    @property
    def is_light(self) -> bool:
        """
        Check if the theme is light.
        """
        return self.base.lower() == "light"


def get_theme() -> ThemeModel:
    """
    Get the theme object to be used in the app.
    """
    return ThemeModel(**st_theme())
