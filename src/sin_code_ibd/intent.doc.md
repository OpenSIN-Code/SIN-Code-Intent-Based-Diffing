# `intent.py` — Intent Summarizer

What this file does: turns a list of `Change` into a one-line human-readable summary, plus a structured `Intent` (category + confidence).

## Dependency map

- Imports: stdlib (`dataclasses`, `typing`); internal: `nodes.Change, ChangeType`.
- Imported by: `__init__.py`, the CLI.

## Public API

| Symbol              | Purpose                                                          |
|---------------------|------------------------------------------------------------------|
| `Intent`            | Frozen dataclass: `category`, `description`, `affected_areas`, `confidence` |
| `IntentSummarizer`  | Class with two summarization methods                             |
| `.CATEGORY_HINTS`   | Class attribute: keyword → category map                          |
| `.summarize(changes)` | Return a one-line string like `"Refactored auth flow, added OAuth"` |
| `.summarize_structured(changes)` | Return an `Intent` object                          |

## Categories

| Category     | Triggering keywords / change types                          |
|--------------|---------------------------------------------------------------|
| `feature`    | add/added/new/introduce keywords, or `ChangeType.ADDED`       |
| `chore`      | remove/removed/delete keywords, or `ChangeType.REMOVED`     |
| `refactor`   | refactor/extract/inline/rename keywords, or REFACTORED/RENAMED |
| `fix`        | fix/bug keywords; fallback for uncategorized MODIFIED         |
| `security`   | security/auth/crypto/payment keywords                         |

## Important config / limits

- **Confidence = `min(1.0, max(0.1, len(changes) / 10))`.** 10 changes saturates to 1.0; 1 change floors to 0.1.
- **First keyword match wins.** Keywords are checked in dict-insertion order; reorder `CATEGORY_HINTS` to change priority.
- **Mixed uncategorizable changes** return `"Mixed changes detected."`.
- **Empty input** returns `"No semantic changes detected."`.

## Design decisions

- **Why keyword matching?** Simpler than training a classifier. False positives are OK — the goal is "good enough summary" for a code-review UI.
- **Why check keywords on `details + name`?** `details` is the human-readable description of the change; `name` is the symbol name. Both carry signal.
- **Why `frozen=True, slots=True` on `Intent`?** Immutable + memory-efficient. `Intent` is created once per summarization and passed around.

## Usage example

```python
from sin_code_ibd import IntentSummarizer

summarizer = IntentSummarizer()
text = summarizer.summarize(changes)
intent = summarizer.summarize_structured(changes)
print(text, intent.category, intent.confidence)
```

## Caveats / footguns

- **The keyword list is English-only.** Add translations by subclassing and overriding `CATEGORY_HINTS`.
- **The default confidence is heuristic.** For higher-quality confidence, train a classifier on labeled data.
- **Empty `details` is a common bug** — pass a populated `details` string for best results.
