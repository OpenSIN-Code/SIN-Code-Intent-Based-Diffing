# `parsers/__init__.py` — Parser Registry

What this file does: the parser package marker. Exposes three concrete parsers (`PythonParser`, `JSParser`, `TSParser`), a `ParserProtocol` (typing-only interface), a `PARSER_REGISTRY` (extension → class), and a `get_parser(path)` factory.

## Dependency map

- Imports: `.python_parser.PythonParser`, `.js_parser.JSParser`, `.ts_parser.TSParser`, stdlib `typing.Protocol`.
- Imported by: `ast_diff.py` (uses `get_parser`).

## Public API

| Symbol              | Purpose                                                          |
|---------------------|------------------------------------------------------------------|
| `ParserProtocol`    | Typing-only interface; all parsers conform                      |
| `PARSER_REGISTRY`   | Dict mapping file extension (lowercase, with dot) → parser class |
| `get_parser(path)`  | Factory: returns a fresh parser for the file's extension        |
| `PythonParser`      | Stdlib-`ast` Python parser                                       |
| `JSParser`          | tree-sitter / regex JS parser                                    |
| `TSParser`          | tree-sitter / regex TS parser (handles `.ts` and `.tsx`)         |

## Extension map

| Extension | Parser            |
|-----------|-------------------|
| `.py`     | `PythonParser`    |
| `.js`     | `JSParser`        |
| `.jsx`    | `JSParser`        |
| `.ts`     | `TSParser`        |
| `.tsx`    | `TSParser`        |
| anything else | `PythonParser` (fallback) |

## Important config / limits

- **Unknown extensions fall back to `PythonParser`.** Add a new extension by extending `PARSER_REGISTRY` before `get_parser` is called.
- **`get_parser` returns a fresh instance** every call. Parsers may hold state (e.g. tree-sitter parser objects) so caching is the caller's responsibility.
- **Lowercase match.** `.PY` and `.Py` resolve to `PythonParser` (Path.suffix is case-sensitive but we lowercase).

## Design decisions

- **Why a registry instead of a `if/elif` chain in `get_parser`?** Easier to extend — adding a new language is a one-line registry update.
- **Why a `ParserProtocol` that's not used at runtime?** Static type checkers (mypy, pyright) can verify that all parsers conform. The runtime cost is zero.

## Usage

```python
from sin_code_ibd.parsers import get_parser

parser = get_parser("src/example.ts")
nodes = parser.parse_file("src/example.ts")
```

## Caveats / footguns

- **The file doesn't need to exist** for `get_parser` to work — only the extension matters. `parse_file` will of course raise if the file is missing.
- **No `register_parser` function** — add entries to `PARSER_REGISTRY` directly.
