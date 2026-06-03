# `parsers/js_parser.py` — JavaScript Parser

What this file does: extracts AST nodes (function declarations, method definitions, class declarations) from JavaScript source. Tries `tree-sitter` first; falls back to a regex on any failure.

## Dependency map

- Imports: stdlib (`pathlib`, `typing`); optional: `tree_sitter`, `tree_sitter_javascript`.
- Imported by: `parsers/__init__.py` (re-export), `ast_diff.py` (via `get_parser`).

## Public API

| Method                                              | Purpose                                                |
|-----------------------------------------------------|--------------------------------------------------------|
| `JSParser()`                                        | Construct; no constructor args                        |
| `.parse_file(path)`                                 | Read `path` and parse; returns `list[dict]`             |
| `.parse_source(source, file_path="")`              | Parse a string; tries tree-sitter, falls back to regex |

## Important config / limits

- **Tree-sitter is optional.** Without it, the regex fallback runs.
- **Regex fallback captures only the declaration line** — `start_line == end_line` and `body is None`. Not suitable for body-aware diffs.
- **Tree-sitter path captures the full body** — `start_line`/`end_line` reflect the actual node range, and `body` is the raw source text.
- **No JSX/TSX support** — that's `TSParser`'s job.

## Design decisions

- **Why try tree-sitter first?** Strict AST, accurate line ranges, full body. The regex is a fallback for environments without `tree-sitter` installed.
- **Why a `try/except` around the entire tree-sitter path?** A single tree-sitter import failure shouldn't break the whole module — the regex fallback is always available.
- **Why no body capture in the regex fallback?** The regex matches only the `function NAME` / `class NAME` line, with no way to find the closing `}` reliably. A line-based fallback is better than a broken body.

## Usage

```python
from sin_code_ibd.parsers import get_parser

parser = get_parser("example.js")
nodes = parser.parse_file("example.js")
```

## Caveats / footguns

- **Tree-sitter parser state is per-instance.** Creating many `JSParser` instances in a tight loop pays the construction cost each time. Cache the parser if you're parsing many files.
- **The regex misses arrow functions and anonymous functions.** Only `function NAME(...)` and `class NAME` patterns are matched.
