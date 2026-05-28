"""
Merge multiple PDFs and split them into two print-ready files
for manual duplex (back-to-back) printing on simplex printers.

Each input PDF is guaranteed to start on an odd page. If needed, a blank page
is inserted so every document begins on the front of a fresh sheet.
"""

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def merge_pdfs_odd_start(pdf_paths: list[Path]) -> PdfWriter:
    """
    Merge all PDFs ensuring each one starts on an odd page.
    A blank page is inserted after any PDF that ends on an odd page
    so the next one always begins on a fresh front-of-sheet.
    """
    writer = PdfWriter()
    for path in pdf_paths:
        reader = PdfReader(str(path))
        page_count = len(reader.pages)

        current_total = len(writer.pages)
        if current_total % 2 != 0:
            print(
                f"  ↳ Inserting blank page before '{path.name}' "
                f"(would start on even page {current_total + 1})"
            )
            writer.add_blank_page()

        start_page = len(writer.pages) + 1
        for page in reader.pages:
            writer.add_page(page)
        end_page = len(writer.pages)

        print(
            f"  + {path.name} ({page_count} pages) → "
            f"merged pages {start_page}–{end_page}"
        )

    return writer


def pad_to_even(writer: PdfWriter) -> int:
    """Add a blank page if total count is odd so duplex math works out."""
    total = len(writer.pages)
    if total % 2 != 0:
        print(f"  ⚠ Odd total page count ({total}), adding a blank page to balance")
        writer.add_blank_page()
        total += 1
    return total


def split_odd_even(writer: PdfWriter, total: int, output_dir: Path):
    """
    Write two output files:
      - print_1_odd.pdf  : pages 1, 3, 5, ...
      - print_2_even.pdf : even pages in reverse order (..., 4, 2)
                           Reversed so page 2 lands on the back of page 1
                           after the stack is flipped.
    """
    odd_writer = PdfWriter()
    for i in range(0, total, 2):
        odd_writer.add_page(writer.pages[i])

    even_writer = PdfWriter()
    for i in range(total - 1, 0, -2):
        even_writer.add_page(writer.pages[i])

    odd_path = output_dir / "print_1_odd.pdf"
    even_path = output_dir / "print_2_even.pdf"

    with open(odd_path, "wb") as f:
        odd_writer.write(f)
    with open(even_path, "wb") as f:
        even_writer.write(f)

    return odd_path, even_path


def resolve_pdf_paths(args: argparse.Namespace) -> tuple[list[Path], Path]:
    """Return (ordered pdf_paths, output_dir) based on parsed args."""
    if args.files:
        pdf_paths = [Path(p) for p in args.files]
        output_dir = pdf_paths[0].parent
    else:
        folder = Path(args.dir)
        if not folder.is_dir():
            print(f"ERROR: Directory not found: {folder}")
            sys.exit(1)
        pdf_paths = sorted(folder.glob("*.pdf"))
        if not pdf_paths:
            print(f"ERROR: No PDF files found in '{folder}'")
            sys.exit(1)
        output_dir = folder

    missing = [p for p in pdf_paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"ERROR: File not found: {m}")
        sys.exit(1)

    return pdf_paths, output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Prepare PDFs for manual duplex printing on a simplex printer."
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="PDF files to merge (in order). Omit to use --dir.",
    )
    parser.add_argument(
        "--dir",
        "-d",
        default="files",
        metavar="DIR",
        help="Folder of PDFs sorted by filename (default: ./files)",
    )
    args = parser.parse_args()

    pdf_paths, output_dir = resolve_pdf_paths(args)

    print(f"\nMerging {len(pdf_paths)} PDF(s) (each starts on an odd page):")
    writer = merge_pdfs_odd_start(pdf_paths)

    total = pad_to_even(writer)
    print(f"\nTotal pages after merge: {total}")

    odd_path, even_path = split_odd_even(writer, total, output_dir)

    print("\n✅ Done!")
    print(f"   {odd_path}  ({total // 2} pages)")
    print(f"   {even_path}  ({total // 2} pages)")
    print("""
─────────────────────────────────────────────
PRINTING INSTRUCTIONS
─────────────────────────────────────────────
1. Print print_1_odd.pdf  → all odd sides
2. Take the stack out of the output tray
3. Flip it:
     • If your printer outputs face-down → flip along the SHORT edge
     • If your printer outputs face-up   → flip along the LONG edge
   (Do a test run with 4 pages first to confirm your printer's behaviour)
4. Put the flipped stack back in the input tray
5. Print print_2_even.pdf → all even sides
─────────────────────────────────────────────
""")
