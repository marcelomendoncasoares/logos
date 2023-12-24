"""
Convert .doc files to .docx and extract its contents to .txt files.

"""

import re

from pathlib import Path

import typer

from doc2docx import convert as convert_doc2docx
from docx2txt import process as convert_docx2txt

# Path to place final .txt files.
DESTINATION_ROOT_PATH = Path("data/prepared/")


app = typer.Typer(no_args_is_help=True)
"""Main CLI app to group commands."""


@app.command()
def extract(path: str = "data/original/books/") -> None:
    """
    Extract text contents from .doc or .docx files. For .doc files, this first
    converts them to .docx files using doc2docx, but removes the converted
    .docx file after the extraction.
    """
    root_path = Path(path)
    convert_doc2docx(root_path)
    for docx_file in root_path.glob("*.docx"):
        output_dir = DESTINATION_ROOT_PATH / docx_file.parent.name
        output_dir.mkdir(parents=True, exist_ok=True)
        txt_path = output_dir / f"{docx_file.stem}.txt"
        txt_path.write_text(convert_docx2txt(docx_file))
        if docx_file.with_suffix(".doc").exists():
            docx_file.unlink()


@app.command()
def clean() -> None:
    """
    Clean up the extracted text files for further processing. The cleaning
    rules are explained in comments above each regex specification.
    """

    CLEANUP_REGEX_SUBSTITUTIONS = [
        # Remove non-breaking spaces and tabs.
        (r"[\u00A0\t]", " "),
        # Remove empty parentheses and brackets.
        (r"[\(\[]\s*[\)\]]", ""),
        # Add missing space after punctuation.
        (r"([\)\],.!?])(\w)", r"\1 \2"),
        # Add missing space before parentheses and brackets.
        (r"(\w)([\(\[])", r"\1 \2"),
        # Replace multiple spaces with single spaces.
        (r" +", " "),
        # Remove hanging space after quotes, parentheses and brackets openers.
        (r"([\u2018\u201C\(\[]) ", r"\1"),
        # Remove hanging space before quotes, parentheses and brackets closers.
        (r" ([\u2019\u201D\)\]])", r"\1"),
        # Replace custom double quotes with standard double quotes.
        (r"[\u2018\u2019\u201C\u201D]", '"'),
        # Replace custom single quotes with standard single quotes.
        (r"[\u201A\u201B]", "'"),
        # Remove spaces on line starts.
        (r"\n([ ]+)", "\n"),
        # Remove spaces on line ends.
        (r"([ ]+)\n", "\n"),
        # Remove lines with only punctuation, spaces or numbers.
        (r"\n([ ,.!?0-9]+)\n", "\n"),
        # Limit the number of newlines to 2.
        (r"\n{3,}", "\n\n"),
        # Remove hanging space before punctuation.
        (r" ([,.!?°º])", r"\1"),
        # Remove duplicated punctuation.
        (r"([,.!?°º])\1+", r"\1"),
        # Remove first line with only numbers.
        (r"^[\d]+\n{2}", ""),
        # Remove last line with only numbers.
        (r"\n{2}[\d]+$", ""),
    ]

    for txt_file in DESTINATION_ROOT_PATH.rglob("*.txt"):
        contents = txt_file.read_text()
        for pattern, replacement in CLEANUP_REGEX_SUBSTITUTIONS:
            contents = re.sub(pattern, replacement, contents)
        txt_file.write_text(contents)


@app.command()
def run(path: str = "data/original/books/") -> None:
    """
    Run all commands in order.
    """
    extract(path)
    clean()


if __name__ == "__main__":
    if not Path(".").resolve().name == "logos":
        raise RuntimeError("Run this script from the root directory.")
    app()
