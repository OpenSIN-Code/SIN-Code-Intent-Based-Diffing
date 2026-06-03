# `parsers/python_parser.py` — Python Parser

What this file does: extracts AST nodes (functions, async functions, classes, imports) from Python source using the stdlib `ast` module. No external dependencies.

## Dependency map

- Imports: stdlib (`ast`, `inspect` — `inspect` is imported but unused; safe to remove), `pathlib`, `typing`.
- Imported by: `parsers/__init__.py`, `ast_diff.py` (via `get_parser`).

## Public API

| Method                                | Purpose                                                                |
|---------------------------------------|------------------------------------------------------------------------|
| `PythonParser()`                      | Construct; no constructor args                                        |
| `.parse_file(path)`                   | Read `path` and parse; returns `list[dict]`                             |
| `.parse_source(source, file_path="")` | Parse a string; raises `SyntaxError` on broken source                  |

## Captured node types

| AST class           | Captured? | Notes                                                          |
|---------------------|-----------|-----------------------------------------------------------------|
| `FunctionDef`       | ✅        | Body + signature + parent (Python 3.12+)                       |
| `AsyncFunctionDef`  | ✅        | Same as `FunctionDef`                                          |
| `ClassDef`          | ✅        | Body + signature + parent (Python 3.12+)                       |
| `Import`            | ✅        | `name` is the comma-joined list of imported modules             |
| `ImportFrom`        | ✅        | `name` is `"<module>: <names>"`                                 |
| All other AST nodes | ❌        | Skipped by `ast.walk()` filter                                  |

## Important config / limits

- **Python 3.12+ only for `parent` tracking.** Earlier versions leave `parent = ""` (parent attribute added in 3.12).
- **`ast.unparse` is Python 3.9+.** On older Python, the signature falls back to `"..."` for args.
- **Body is `None` for imports** — they're single-line statements.
- **Results are sorted by `start_line`** for stable downstream diffing.

## Design decisions

- **Why use stdlib `ast` only?** Zero deps. `ast` is the canonical Python AST.
- **Why sort by start line?** Diff operations need stable input order. `ast.walk()` doesn't guarantee it.
- **Why include imports?** `RiskScorer` flags new imports as a risk factor. Including them here is cheap.

## Usage

```python
from sin_code_ibd.parsers import get_parser

parser = get_parser("example.py")
nodes = parser.parse_file("example.py")
```

## Caveats / footguns

- **`parse_source` raises `SyntaxError`** on broken source. The caller (`ASTDiff.diff_files`) doesn't catch this — broken source is a hard error.
- **`inspect` is imported but unused.** Pre-existing; safe to remove in a future cleanup.
- **The `parent` attribute requires Python 3.12+.** On older versions, RENAMED detection (in `ast_diff.py`) will never fire.
