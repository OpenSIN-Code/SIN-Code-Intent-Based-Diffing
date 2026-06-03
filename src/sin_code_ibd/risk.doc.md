# `risk.py` — Risk Scorer

What this file does: assigns a 0.0–1.0 risk score to a list of `Change` objects, with per-factor breakdown. Six risk factors, each with a fixed weight.

## Dependency map

- Imports: stdlib (`dataclasses`, `typing`); internal: `nodes.Change, ChangeType`.
- Imported by: `__init__.py`, `report.py`, the CLI.

## Public API

| Symbol         | Purpose                                                          |
|----------------|------------------------------------------------------------------|
| `RiskReport`   | Mutable dataclass: `total_risk`, `factors`, `hot_files`, `breakdown` |
| `RiskScorer`   | Class with `.score(changes) → RiskReport`                         |
| `SECURITY_KEYWORDS` | Class attribute: extend in subclasses to add domains        |

## Risk factors

| Factor                | Weight | Triggered when                                              |
|-----------------------|--------|-------------------------------------------------------------|
| `signature_change`    | 0.7    | MODIFIED with `before.signature != after.signature`         |
| `removed_public_api`  | 0.9    | REMOVED with `is_public()`                                  |
| `large_change`        | 0.6    | `loc_delta() > 100`                                          |
| `high_fan_in`         | 0.5    | 3+ changes in the same file                                 |
| `new_dependencies`    | 0.4    | ADDED with `node_type` in `(Import, ImportFrom)`            |
| `security_sensitive`  | 0.85   | `node.name` or `details` matches a `SECURITY_KEYWORDS` term  |

## Total risk formula

```
total = 0.6 * max(scores) + 0.4 * mean(scores)
```

Clamped to [0.0, 1.0]. The `0.6` weight on `max` makes the worst single factor dominant; the `0.4` on the mean adds a "breadth" signal.

## Important config / limits

- **`max` per factor, not `sum`** — a single big change doesn't drown out smaller ones in a different dimension.
- **`SECURITY_KEYWORDS` is case-insensitive** (lower-cased before check). Extend in subclasses for domain-specific terms (e.g. `"pii"`, `"gdpr"`).
- **`high_fan_in` threshold: 3 changes per file.** Below 3, no fan-in signal.
- **`large_change` threshold: 100 LOC delta.** Below 100, not flagged.

## Design decisions

- **Why weighted max + mean?** A single critical change (max=0.9) should dominate a few small ones. The mean adds a "lots of small issues" signal without overwhelming the max.
- **Why are the per-factor weights hard-coded?** They're tuned for a code-review UI. If your domain needs different weights, subclass `RiskScorer` and override `score()`.
- **Why `frozen=False` on `RiskReport`?** Callers can post-process (e.g. add custom factors) without rebuilding.

## Usage

```python
from sin_code_ibd import ASTDiff, RiskScorer

changes = ASTDiff().diff_files("before.py", "after.py")
report = RiskScorer().score(changes)
print(f"Total risk: {report.total_risk}")
print(f"Hot files: {report.hot_files}")
```

## Caveats / footguns

- **The risk score is a heuristic.** Don't use it as a deployment gate without calibrating against your codebase.
- **Threshold values (100 LOC, 3 changes) are arbitrary.** Tune for your domain.
- **`hot_files` may include the same file under multiple factors** — the `set` deduplication happens per factor, but the output is a sorted list of distinct paths.
