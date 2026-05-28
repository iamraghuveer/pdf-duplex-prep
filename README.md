# pdf-duplex-prep

Merge multiple PDFs and split them into two print-ready files for manual duplex (double-sided) printing on simplex (one-sided) printers.

Each input PDF is guaranteed to start on an odd page. If needed, a blank page is automatically inserted so every document begins on the front of a fresh sheet.

## Usage

```bash
# Reads all PDFs from ./files/, sorted by name
python main.py

# Reads all PDFs from a specific folder, sorted by name
python main.py --dir path/to/folder

# Explicit files in a specific order
python main.py doc1.pdf doc2.pdf doc3.pdf
```

### Output

Two files are written to the input folder:

| File | Contents |
|------|----------|
| `print_1_odd.pdf` | Pages 1, 3, 5, … — print this first |
| `print_2_even.pdf` | Even pages in reverse order — print this second |

## Printing instructions

1. Print `print_1_odd.pdf` (all odd sides)
2. Remove the stack from the output tray
3. Flip the stack:
   - Printer outputs **face-down** → flip along the **short** edge
   - Printer outputs **face-up** → flip along the **long** edge

   > Run a test with 4 pages first to confirm your printer's behaviour.
4. Return the flipped stack to the input tray
5. Print `print_2_even.pdf` (all even sides)

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py --dir path/to/your/pdfs
```

Or with plain pip:

```bash
pip install pypdf
python main.py --dir path/to/your/pdfs
```
