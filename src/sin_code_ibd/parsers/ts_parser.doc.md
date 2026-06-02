# `ts_parser.py` — TypeScript Parser

What this file does: extracts AST nodes from TypeScript source using tree-sitter or regex fallback.

## Dependencies

- Imported by: `parsers/__init__.py`, tests

## Public API

- `TSParser()` — TypeScript parser
- `parse_file(path)` → list[dict]
- `parse_source(source, file_path)` → list[dict]

## Notes

Requires `tree-sitter` and `tree-sitter-typescript` for full parsing. Falls back to regex-based heuristic if tree-sitter is unavailable.
