# `report.py` — Diff Report Formatter

What this file does: formats semantic changes into human-readable reports (text, JSON, markdown).

## Dependencies

- Imported by: tests, CLI
- Imports: `nodes` (Change, ChangeType)

## Usage

```python
from sin_code_ibd.report import DiffReport
report = DiffReport.from_changes(changes)
print(report.to_markdown())
```

## Notes

Reports include a summary table with change counts per category.
