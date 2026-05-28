# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Single-purpose Python utility that prepares multiple PDFs for manual duplex (double-sided) printing on simplex (one-sided) printers. It merges PDFs with odd-page-start alignment, then splits the result into two ordered print files.

## Commands

This project uses `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Run against all PDFs in ./files/, sorted by name (default)
uv run pdf-duplex-prep

# Run against a specific folder
uv run pdf-duplex-prep --dir path/to/folder

# Run with explicit files in a specific order
uv run pdf-duplex-prep doc1.pdf doc2.pdf doc3.pdf

# Run tests
uv run pytest tests/ -v
```

Output files (`print_1_odd.pdf`, `print_2_even.pdf`) are written into the input folder.

## Architecture

All logic lives in `pdf_duplex_prep/__init__.py`. The pipeline is three steps:

1. **`merge_pdfs_odd_start`** — appends PDFs sequentially, inserting a blank page before any that would otherwise start on an even page number.
2. **`pad_to_even`** — ensures the final merged document has an even page count so the duplex math is consistent.
3. **`split_odd_even`** — writes `print_1_odd.pdf` (pages 1, 3, 5, …) and `print_2_even.pdf` (even pages in **reverse** order: last_even, …, 4, 2). The reversal is intentional: after printing odd pages and flipping the stack, the reversed even pages align correctly for back-to-back printing.

## Releasing

Tag a commit to trigger the PyPI publish workflow:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Requires trusted publishing (OIDC) configured on PyPI for this repo, with workflow filename `publish.yml` and no environment name.
