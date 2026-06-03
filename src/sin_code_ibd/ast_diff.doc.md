# `ast_diff.py` — Semantic Diffing Engine

What this file does: the diffing engine. Compares two files or two directories and returns a list of `Change` objects, each tagged with a `ChangeType` (ADDED / REMOVED / MODIFIED / RENAMED / REFACTORED). The goal is "good enough signal" for a code-review UI, not formal equivalence.

## Dependency map

- Imports: stdlib (`difflib`, `os`, `pathlib`, `typing`); internal: `nodes`, `parsers.get_parser`.
- Imported by: `__init__.py`, `cli.py` (in `sin-code-review-interface`).

## Public API

| Method                       | Purpose                                                          |
|------------------------------|------------------------------------------------------------------|
| `ASTDiff(parser="auto")`     | Construct; `"auto"` picks from the file extension                 |
| `.diff_files(path_a, path_b)`| Diff two files; returns `list[Change]`                            |
| `.diff_dirs(dir_a, dir_b)`   | Recursively diff two directories (matched by relative path)      |

## Change classification (in order of precedence)

1. **RENAMED** — `parent` changed but `body` identical.
2. **REFACTORED** — `signature` identical, both bodies >5 lines, line-similarity between 30% and 100%.
3. **MODIFIED** — `signature` or `body` changed.
4. **ADDED** — exists only in the "after" side.
5. **REMOVED** — exists only in the "before" side.

## Important config / limits

- **REFACTORED requires both bodies >5 lines.** Below that, even a substantial rewrite is MODIFIED.
- **Refactor similarity is 30%–100%.** Identical (100%) is a no-op; <30% is a rewrite (MODIFIED).
- **`diff_dirs` matches by relative path.** Two files with the same name in different subdirs are diffed independently.
- **Symlinks are NOT followed** — `rglob` is used as-is.

## Design decisions

- **Why classify RENAMED before REFACTORED?** They're disjoint (RENAMED keeps body; REFACTORED rewrites it), but checking RENAMED first short-circuits the expensive body-similarity check.
- **Why use `difflib.SequenceMatcher` for refactor detection?** It handles multi-line bodies without needing line-by-line pre-processing.
- **Why is body capture conditional?** The regex fallback for JS/TS doesn't capture body (only the declaration line). Tree-sitter captures the full body.

## Usage example

```python
from sin_code_ibd import ASTDiff

differ = ASTDiff()
changes = differ.diff_files("before.py", "after.py")
for c in changes:
    print(c.change_type.name, c.node.name, "at", c.node.file_path)
```

## Caveats / footguns

- **Bodies are NOT captured for JS/TS in regex fallback mode** — `start_line == end_line` and `body is None`. Tree-sitter is the fix.
- **Two functions with the same name in the same file** (e.g. a method and a free function) collide. DiffNode uses `name` as the unique key.
- **No `parent` tracking on Python < 3.12** — the AST's `parent` attribute was added in 3.12. RENAMED detection on older Pythons falls back to `parent = ""` on both sides → never RENAMED.
