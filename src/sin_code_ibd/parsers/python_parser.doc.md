# `python_parser.py` — Python Parser

What this file does: extracts AST nodes from Python source using the stdlib `ast` module.

## Dependencies

- Imported by: `parsers/__init__.py`, tests

## Public API

- `PythonParser()` — Python parser
- `parse_file(path)` → list[dict]
- `parse_source(source, file_path)` → list[dict]

## Notes

Uses `ast.walk()` to find all function, class, and import nodes. Sorts results by start line for stable ordering.
