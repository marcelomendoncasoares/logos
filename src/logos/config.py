"""
Configurations for the logos app.
"""

import os

from pathlib import Path

from pydantic import BaseModel


class ModelInstructionsConfig(BaseModel):
    """
    Configuration for the model instructions.
    """

    query: str = ""
    data: str = ""


class Config:
    """
    Singleton class to store configurations.
    """

    ROOT_FOLDER = Path(os.environ.get("LOGOS_ROOT_FOLDER", Path.home() / ".logos"))
    """Root folder for the application."""

    MODEL_PATH = "intfloat/multilingual-e5-large"
    """Default embedding model path."""

    MODEL_INSTRUCTIONS = ModelInstructionsConfig(
        query="query: ",
        data="data: ",
    )
    """Instructions for the default model to prepend queries and texts."""
