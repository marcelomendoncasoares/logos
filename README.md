<h1 align="center">Logos</h1>
<p align="center">
  <a href="https://github.com/marcelomendoncasoares">
    <img alt="GitHub" src="https://img.shields.io/badge/GitHub-marcelomendoncasoares-181717.svg?style=flat&logo=github" />
  </a>
  <!-- <a href="https://pypi.org/project/logos">
    <img alt="Python" src="https://img.shields.io/pypi/pyversions/logos.svg" />
  </a> -->
  <!-- <a href="https://pypi.org/project/logos/">
    <img alt="PyPI" src="https://badge.fury.io/py/logos.svg" />
  </a> -->
  <a href="https://github.com/marcelomendoncasoares/logos/blob/main/LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-purple.svg" target="_blank" />
  </a>
  <!-- <a href="https://github.com/marcelomendoncasoares/logos/actions/workflows/validate.yml">
    <img alt="tests" src="https://github.com/marcelomendoncasoares/logos/actions/workflows/validate.yml/badge.svg?branch=main" />
  </a> -->
  <!-- <a href="https://github.com/marcelomendoncasoares/logos/actions/workflows/release.yml">
    <img alt="build" src="https://github.com/marcelomendoncasoares/logos/actions/workflows/release.yml/badge.svg?branch=main" />
  </a> -->
  <!-- <a href="https://codecov.io/gh/marcelomendoncasoares/logos" >
    <img src="https://codecov.io/gh/marcelomendoncasoares/logos/branch/main/graph/badge.svg?token=<TOKEN_HERE>"/>
  </a> -->
  <a href="https://github.com/pre-commit/pre-commit">
    <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white">
  </a>
  <a href="https://github.com/astral-sh/ruff" >
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"/>
  </a>
  <a href="http://mypy-lang.org/">
    <img alt="Checked with mypy" src="http://www.mypy-lang.org/static/mypy_badge.svg">
  </a>
  <a href="https://github.com/psf/black">
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
  </a>
</p>

> An application for robust search of Logosophy teachings powered by LLMs and
> classical techniques. This tool also aims to simplify a crucial part of
> logosophy study, which is the preparation of specific study programs from the
> vast amount of material available.

- [Usage](#usage)
  - [Indexing documents](#indexing-documents)
  - [Searching for topics on the CLI](#searching-for-topics-on-the-cli)
- [Next steps](#next-steps)
  - [Streamlit Search App](#streamlit-search-app)
  - [Search Engine](#search-engine)
  - [Study programs App feature](#study-programs-app-feature)
  - [CLI tool](#cli-tool)
- [Contributing](#contributing)

---

# Usage

Although the web application is not yet available, it is possible to use the
CLI tool to index documents and search for specific topics. The `logos` command
serves as entry point for the CLI. This tool is part of the package and will
always be the interface for indexing documents.

## Indexing documents

To index a document, use the `index` command followed by the path to the
document. All documents are expected to be in `Markdown` format, regardless of
the file extension. The tool will extract the paragraphs from the document and
store together with the headers and document title.

```bash
logos index 'data/prepared/'
```

The command allow filtering the files and will recursively search for documents
in the given path. For more information on the command options, use the
`--help` flag.

## Searching for topics on the CLI

To search for a specific topic, use the `search` command followed by the query
you want to search for. The tool will return a list of paragraph passages that
are related to the query using both dense, sparse and keyword search.

```bash
logos search "Como asimilar la enseñanza logosófica?" --limit 10
```

The command will display the most relevant passages, together with the score
related to the query and the metadata of the passage (file, section headers,
paragraphs, etc).

# Next steps

## Streamlit Search App

- [x] ~~Build a first app version that allows the user to search for a specific
      topic and get a list of paragraphs that contain the topic.~~
- [x] ~~Add a button to copy the paragraph to the clipboard with citation for
      easy usage in study programs.~~
- [ ] Allow the user to select only `dense`, only `sparse` or only `keyword`
      search while performing a query.
- [x] ~~Paginate the search results to show only a few paragraphs
      (configurable) per page to improve the loading time.~~
- [ ] If the passage is only a fragment of a paragraph, show the full paragraph
      instead, with the fragment highlighted.
- [ ] Add highlighting to the parts of each passage that justify its position
      on the search results (maybe use LLM to score indicate relevant parts).
- [ ] Allow the user to click on a search result and see the surrounding
      paragraphs, scrolling through them as if viewing the original source.
- [ ] Add a verification to correct eventually mistyped queries, either using
      levenstein distance or an LLM model.
- [ ] Add autocomplete suggestions for the search bar while the user types.
- [ ] Add a chat with a `Retriever` chatbot that helps the user to find the
      most relevant paragraphs for a specific topic.

## Search Engine

- [ ] Add a cross-encoder to re-rank search results.
- [ ] Test the `multilingual-e5-large-instruct` model for the search engine.
- [ ] Improve sparse search by using chars n-grams to split words
      ([reference](https://medium.com/@emitchellh/extending-bm25-with-subwords-30b334728ebd)).
- [ ] Replace `txtai` by `llama-index` for a more robust resources ecosystem.
- [ ] Build a knowledge-graph extracting triplets from the paragraphs.
- [ ] Add a `deep search` mechanism that runs a query, extracts top-k terms
      from the found results, creates N new queries similar to the original but
      using the top-k terms, and re-rank the results using the cross-encoder.

## Study programs App feature

- [ ] Add study program creations.
- [ ] Allow the user to select a paragraph and add it to a study program.
- [ ] Add login to save study programs per user.
- [ ] Allow management of saved study programs.

## CLI tool

- [x] ~~Speed up the imports for a quicker CLI loading (specially for --help
      calls)~~.
- [ ] Move the `doc2docx` script to the CLI as a utility.

# Contributing

Simply install the package using poetry:

```bash
pip install poetry
poetry install
```

To contribute, make sure to install the pre-commit hooks and run the tests
before submitting a pull request.

```bash
pre-commit install
pre-commit run --all-files
```
