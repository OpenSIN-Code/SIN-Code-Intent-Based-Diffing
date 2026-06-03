# `nodes.py` — Core Data Types

What this file does: the data model for semantic diffing. Three types: `ChangeType` (enum), `DiffNode` (immutable AST node from one side), `Change` (mutable delta).

## Dependency map

- Imports: stdlib (`dataclasses`, `enum`, `typing`).
- Imported by: `ast_diff.py`, `intent.py`, `risk.py`, `report.py`.

## Public API

| Symbol         | Mutability    | Purpose                                                          |
|----------------|---------------|------------------------------------------------------------------|
| `ChangeType`   | enum          | ADDED / REMOVED / MODIFIED / RENAMED / REFACTORED                |
| `DiffNode`     | frozen + slots| An AST node from one side of a diff                              |
| `Change`       | mutable + slots | A delta between two sides (or an add/remove)                   |

### `DiffNode` fields

| Field          | Type        | Notes                                                          |
|----------------|-------------|----------------------------------------------------------------|
| `node_type`    | `str`       | AST class name (`FunctionDef`, `ClassDef`, `Import`, …)        |
| `name`         | `str`       | Identifier (function/class/import name)                        |
| `file_path`    | `str`       | Path to the source file                                         |
| `start_line`   | `int`       | 1-based, inclusive                                              |
| `end_line`     | `int`       | 1-based, inclusive                                              |
| `body`         | `str\|None` | Source text (None for imports and regex-parsed JS/TS)            |
| `signature`    | `str\|None` | `def f(x, y)` / `class C(Base)` form (Python only)               |
| `parent`       | `str\|None` | Parent symbol name (Python 3.12+ only)                          |

### `Change` methods

| Method         | Returns       | Purpose                                                          |
|----------------|---------------|------------------------------------------------------------------|
| `is_public()`  | `bool`        | True iff `name` doesn't start with `_`                            |
| `loc_delta()`  | `int`         | Approximate lines of code changed (0 for ADDED/REMOVED with no before/after) |

## Important config / limits

- **`DiffNode.body` is `None`** for regex-parsed JS/TS or imports.
- **`Change.before` / `after`** are populated only for MODIFIED / RENAMED / REFACTORED.
- **Underscore-prefixed names** are considered private (Python convention).

## Design decisions

- **Why `frozen=True, slots=True` on `DiffNode`?** Immutable + memory-efficient. DiffNodes are produced once by the parsers and passed around.
- **Why `frozen=False` on `Change`?** Callers can post-process (e.g. add custom fields) without rebuilding the object.
- **Why is `parent` only on Python 3.12+?** The `ast` module's `parent` attribute was added in 3.12. On older versions it's `None` for all nodes.

## Usage

```python
from sin_code_ibd import ChangeType, Change, DiffNode

n = DiffNode(node_type="FunctionDef", name="foo", file_path="a.py", start_line=1, end_line=5)
c = Change(change_type=ChangeType.ADDED, node=n, details="Added function foo")
print(c.is_public(), c.loc_delta())  # True, 5
```

## Caveats / footguns

- **`Change.is_public` only checks the name.** A symbol like `__init__` (dunder) is also considered public. Add explicit checks if you need dunder-aware logic.
- **`loc_delta` is an approximation.** It uses AST line ranges, not actual source-line deltas after formatting.
