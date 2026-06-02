# `__init__.py` — Parsers Package

What this file does: auto-detects language from file extension and returns the appropriate parser.

## Dependencies

- Imported by: `ast_diff.py`, tests

## Exports

- `ParserProtocol` — shared interface for all parsers
- `PARSER_REGISTRY` — mapping of file extension to parser class
- `get_parser(path)` — return a parser instance based on file extension
- `PythonParser`, `JSParser`, `TSParser` — concrete parser classes

## Usage

```python
from sin_code_ibd.parsers import get_parser
parser = get_parser("app.py")
```

## Notes

Default parser is `PythonParser` for unknown extensions.
