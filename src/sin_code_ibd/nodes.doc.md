# `nodes.py` — Diff Data Structures

What this file does: defines the core data types used by the diff engine: `DiffNode`, `Change`, `ChangeType`.

## Dependencies

- Imported by: `ast_diff.py`, `intent.py`, `risk.py`, `report.py`, tests

## Types

- `DiffNode` — AST node with name, type, signature, body, parent, file_path
- `Change` — a semantic change with before/after nodes and metadata
- `ChangeType` — enum: ADDED, REMOVED, MODIFIED, RENAMED, REFACTORED

## Usage

```python
from sin_code_ibd.nodes import Change, ChangeType, DiffNode
```

## Notes

`Change.is_public()` checks if the node name does not start with `_`.
