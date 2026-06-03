# `report.py` — Report Formatting

What this file does: a single `ReportFormatter` class with three static methods that render `Change` lists, `RiskReport` objects, and arbitrary data as text or JSON. Designed for CLI / log output.

## Dependency map

- Imports: stdlib (`json`, `typing`); internal: `nodes`, `risk`, `intent`.
- Imported by: the CLI (`sin-code-review-interface`), external scripts.

## Public API

| Method                                       | Purpose                                                          |
|----------------------------------------------|------------------------------------------------------------------|
| `ReportFormatter.format_changes(changes)`     | Multi-line text: one block per `Change`                          |
| `ReportFormatter.format_risk(report)`         | Multi-line text: total risk + breakdown + factors + hot files    |
| `ReportFormatter.to_json(data)`               | Pretty JSON with a custom default for unknown objects             |

## Important config / limits

- **`to_json` falls back to `str(o)`** for objects without `__dict__`. This covers most dataclasses but not enums or sets.
- **No HTML / rich UI** — these are plain text. Render to a different format in the consumer.

## Design decisions

- **Why static methods?** `ReportFormatter` is a namespace, not a stateful object. The methods don't share state.
- **Why a `default` lambda in `to_json`?** A `RiskReport` or `Change` is a dataclass — `json.dumps` doesn't know how to serialize it. The default falls back to `__dict__`.

## Usage

```python
from sin_code_ibd import ASTDiff
from sin_code_ibd.report import ReportFormatter

changes = ASTDiff().diff_files("before.py", "after.py")
print(ReportFormatter.format_changes(changes))
print(ReportFormatter.to_json(changes))
```

## Caveats / footguns

- **`format_risk` shows every factor even if score is 0** — useful for "here's what I checked" transparency, but verbose.
- **`to_json` doesn't preserve enum values** — they'll be rendered as their string name (or `str(o)`).
