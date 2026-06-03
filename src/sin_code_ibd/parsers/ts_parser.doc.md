# `parsers/ts_parser.py` — TypeScript Parser

What this file does: extracts AST nodes (function declarations, method definitions, class declarations, interface declarations) from TypeScript source. Tries `tree-sitter-typescript` first; falls back to a regex on any failure.

## Dependency map

- Imports: stdlib (`pathlib`, `typing`); optional: `tree_sitter`, `tree_sitter_typescript`.
- Imported by: `parsers/__init__.py`, `ast_diff.py` (via `get_parser`).

## Public API

| Method                                | Purpose                                                |
|---------------------------------------|--------------------------------------------------------|
| `TSParser()`                          | Construct; no constructor args                        |
| `.parse_file(path)`                   | Read `path` and parse; returns `list[dict]`             |
| `.parse_source(source, file_path="")` | Parse a string; tries tree-sitter, falls back to regex |

## Important config / limits

- **Tree-sitter is optional.** Without it, the regex fallback runs.
- **TSX support** — uses the TSX grammar when `file_path` ends with `.tsx`, so JSX inside `<…>` parses correctly.
- **Regex fallback captures only the declaration line** — `start_line == end_line` and `body is None`.
- **Captures 4 node types**: function, method, class, interface. The regex matches `(?:function|class|interface) NAME`.

## Design decisions

- **Why separate the TSX grammar?** TSX files embed JSX expressions that the plain TypeScript grammar doesn't understand. Switching to the TSX grammar avoids parse errors.
- **Why include interfaces in the regex?** Interfaces are first-class in TypeScript; missing them would miss a large class of declarations.
- **Why does the regex set `node_type` from a `keyword → type` dict?** Cleanly handles three keywords without nested conditionals. The previous chained-ternary was harder to read.

## Usage

```python
from sin_code_ibd.parsers import get_parser

parser = get_parser("example.ts")
nodes = parser.parse_file("example.ts")
```

## Caveats / footguns

- **Tree-sitter parser state is per-instance.** Cache the parser if you're parsing many files.
- **The regex misses type aliases** (`type Foo = ...`) and `enum` declarations. Only the three explicit keywords are matched.
- **The grammar choice is by `file_path` extension only.** If you pass a `.ts` file but the path doesn't end in `.tsx`, the plain TS grammar is used (which can fail on JSX syntax).
