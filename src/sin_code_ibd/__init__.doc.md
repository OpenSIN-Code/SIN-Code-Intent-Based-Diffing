# `__init__.py` — Public Package API

What this file does: re-exports the public symbols of `sin_code_ibd` so users can do `from sin_code_ibd import ASTDiff, IntentSummarizer, ...`.

## Dependency map

- Imports: `.ast_diff.ASTDiff`, `.intent.IntentSummarizer`, `.risk.RiskScorer, RiskReport`, `.nodes.DiffNode, ChangeType, Change`.
- Imported by: external user code, the CLI (`sin-code-review-interface`).

## Public API

```python
from sin_code_ibd import (
    ASTDiff,               # the diffing engine
    IntentSummarizer,      # human-readable intent summaries
    RiskScorer,            # numeric risk assessment
    RiskReport,            # the result of a risk score
    DiffNode,              # an AST node from one side
    Change,                # a delta between two sides
    ChangeType,            # enum: ADDED/REMOVED/MODIFIED/RENAMED/REFACTORED
)
```

## Caveats / footguns

- Adding a new top-level class? Update `__all__` here or `import *` callers won't see it.
- The package has no `__version__`; pin to a git ref or read `pyproject.toml`.
