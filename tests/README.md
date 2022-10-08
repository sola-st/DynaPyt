# Tests

This directory contains *micro-tests* that each consist of
 * A small example program, stored in a file called `program.py`
 * A simple analysis, stored in a file called `analysis.py`, that uses a small set of hooks to either analyze or manipulate the program's execution
 * A file called `expected.txt` with the console output expected to be produced when `analysis.py` is applied to `program.py`

Each micro-test is stored in a separate subdirectory of this directory.

Run all tests with:
```
pytest tests
```