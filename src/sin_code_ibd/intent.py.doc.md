# intent.py

What does this file do? IntentSummarizer translates a list of semantic changes into a human-readable intent string (e.g., "Added feature foo and bar").

Which other files import / touch it? `__init__.py` exports IntentSummarizer. Tests in `tests/test_intent.py` cover it.

Important config values & limits: CATEGORY_HINTS map keywords to categories (feature, refactor, fix, security, chore).

Why certain decisions were made: Simple keyword-based heuristics are fast and deterministic. Structured output (`Intent` dataclass) is available for programmatic consumers.

Usage examples: `IntentSummarizer().summarize(changes)`

Known caveats or footguns: Keyword detection is naive; complex multi-file refactor intents may need manual review.
