# `__init__.py` — SIN-Code Intent-Based Diffing

What this file does: package-level exports for `sin_code_ibd`.

## Dependencies

- Imported by: external consumers, tests, CLI, MCP server
- Imports: `ast_diff`, `intent`, `risk`, `nodes`

## Exports

- `ASTDiff` — semantic diff engine
- `IntentSummarizer` — human-readable intent from changes
- `RiskScorer` — risk assessment for change sets
- `RiskReport` — structured risk report
- `DiffNode`, `ChangeType`, `Change` — diff data structures

## Usage

```python
from sin_code_ibd import ASTDiff, IntentSummarizer, RiskScorer
```

## Notes

Keep `__all__` in sync with the public API to avoid leaking internals.
