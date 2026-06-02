# `js_parser.py` — JavaScript Parser

What this file does: extracts AST nodes from JavaScript source using tree-sitter or regex fallback.

## Dependencies

- Imported by: `parsers/__init__.py`, tests

## Public API

- `JSParser()` — JavaScript parser
- `parse_file(path)` → list[dict]
- `parse_source(source, file_path)` → list[dict]

## Notes

Requires `tree-sitter` and `tree-sitter-javascript` for full parsing. Falls back to regex-based heuristic if tree-sitter is unavailable.
