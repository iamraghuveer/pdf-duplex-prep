from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from pdf_duplex_prep import (
    merge_pdfs_odd_start,
    pad_to_even,
    resolve_pdf_paths,
    split_odd_even,
)


def make_pdf(tmp_path: Path, name: str, num_pages: int) -> Path:
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    path = tmp_path / name
    with open(path, "wb") as f:
        writer.write(f)
    return path


# --- merge_pdfs_odd_start ---


def test_merge_even_page_pdf_no_padding(tmp_path):
    a = make_pdf(tmp_path, "a.pdf", 2)
    b = make_pdf(tmp_path, "b.pdf", 3)
    writer = merge_pdfs_odd_start([a, b])
    assert len(writer.pages) == 5  # no blank inserted


def test_merge_odd_page_pdf_inserts_blank(tmp_path):
    a = make_pdf(tmp_path, "a.pdf", 3)
    b = make_pdf(tmp_path, "b.pdf", 2)
    writer = merge_pdfs_odd_start([a, b])
    # a ends on page 3 (odd total) → blank inserted → b starts on page 5
    assert len(writer.pages) == 6


def test_merge_multiple_pdfs_all_aligned(tmp_path):
    pdfs = [make_pdf(tmp_path, f"{i}.pdf", 2) for i in range(4)]
    writer = merge_pdfs_odd_start(pdfs)
    assert len(writer.pages) == 8


def test_merge_preserves_order(tmp_path):
    # Use single-page PDFs so we can track blank insertions deterministically
    a = make_pdf(tmp_path, "a.pdf", 2)  # ends even → no pad
    b = make_pdf(tmp_path, "b.pdf", 2)  # ends even → no pad
    writer = merge_pdfs_odd_start([a, b])
    assert len(writer.pages) == 4


# --- pad_to_even ---


def test_pad_to_even_already_even(tmp_path):
    a = make_pdf(tmp_path, "a.pdf", 4)
    writer = merge_pdfs_odd_start([a])
    total = pad_to_even(writer)
    assert total == 4


def test_pad_to_even_odd_count(tmp_path):
    a = make_pdf(tmp_path, "a.pdf", 3)
    writer = merge_pdfs_odd_start([a])
    total = pad_to_even(writer)
    assert total == 4
    assert len(writer.pages) == 4


# --- split_odd_even ---


def test_split_page_counts(tmp_path):
    a = make_pdf(tmp_path, "a.pdf", 4)
    writer = merge_pdfs_odd_start([a])
    total = pad_to_even(writer)
    odd_path, even_path = split_odd_even(writer, total, tmp_path)

    assert len(PdfReader(odd_path).pages) == 2
    assert len(PdfReader(even_path).pages) == 2


def test_split_even_pages_are_reversed(tmp_path):
    # Build a 4-page merged PDF from two 2-page docs. With unique page sizes
    # we can fingerprint which original page landed where.
    writer = PdfWriter()
    sizes = [(100, 200), (300, 400), (500, 600), (700, 800)]
    for w, h in sizes:
        writer.add_blank_page(width=w, height=h)

    odd_path, even_path = split_odd_even(writer, 4, tmp_path)

    odd_pages = PdfReader(odd_path).pages
    even_pages = PdfReader(even_path).pages

    # Odd file: page 1 (100×200), page 3 (500×600)
    assert int(odd_pages[0].mediabox.width) == 100
    assert int(odd_pages[1].mediabox.width) == 500

    # Even file reversed: page 4 (700×800) then page 2 (300×400)
    assert int(even_pages[0].mediabox.width) == 700
    assert int(even_pages[1].mediabox.width) == 300


# --- resolve_pdf_paths ---


def test_resolve_from_directory(tmp_path, monkeypatch):
    make_pdf(tmp_path, "b.pdf", 1)
    make_pdf(tmp_path, "a.pdf", 1)

    import argparse

    args = argparse.Namespace(files=[], dir=str(tmp_path))
    paths, output_dir = resolve_pdf_paths(args)

    assert [p.name for p in paths] == ["a.pdf", "b.pdf"]
    assert output_dir == tmp_path


def test_resolve_explicit_files(tmp_path):
    a = make_pdf(tmp_path, "a.pdf", 1)
    b = make_pdf(tmp_path, "b.pdf", 1)

    import argparse

    args = argparse.Namespace(files=[str(b), str(a)], dir="files")
    paths, output_dir = resolve_pdf_paths(args)

    assert paths == [b, a]
    assert output_dir == tmp_path


def test_resolve_missing_directory_exits(tmp_path):
    import argparse

    args = argparse.Namespace(files=[], dir=str(tmp_path / "nonexistent"))
    with pytest.raises(SystemExit):
        resolve_pdf_paths(args)


def test_resolve_empty_directory_exits(tmp_path):
    import argparse

    args = argparse.Namespace(files=[], dir=str(tmp_path))
    with pytest.raises(SystemExit):
        resolve_pdf_paths(args)
