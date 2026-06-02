"""IntentSummarizer — generate human-readable intent from changes.

Docs: src/sin_code_ibd/intent.py.doc.md
"""

from __future__ import annotations
import dataclasses
from typing import Any

from .nodes import Change, ChangeType


@dataclasses.dataclass(frozen=True, slots=True)
class Intent:
    """Structured intent extracted from a change set."""
    category: str          # e.g. 'feature', 'refactor', 'fix', 'chore'
    description: str       # human-readable one-liner
    affected_areas: list[str]
    confidence: float      # 0.0-1.0


class IntentSummarizer:
    """Summarize a list of semantic changes into a human-readable intent string."""

    # Keywords mapped to categories
    CATEGORY_HINTS: dict[str, str] = {
        "add": "feature",
        "added": "feature",
        "new": "feature",
        "introduce": "feature",
        "remove": "chore",
        "removed": "chore",
        "delete": "chore",
        "refactor": "refactor",
        "extract": "refactor",
        "inline": "refactor",
        "rename": "refactor",
        "fix": "fix",
        "bug": "fix",
        "security": "security",
        "auth": "security",
        "crypto": "security",
        "payment": "security",
    }

    def summarize(self, changes: list[Change]) -> str:
        """Returns human-readable intent like 'Refactored auth flow, added OAuth support'."""
        if not changes:
            return "No semantic changes detected."

        categories = self._categorize(changes)
        parts: list[str] = []
        for cat, items in categories.items():
            action = self._action_for_category(cat)
            names = [c.node.name for c in items if c.node.name]
            if names:
                summary = f"{action} {cat} {self._pretty_list(names)}"
                parts.append(summary)

        if not parts:
            return "Mixed changes detected."
        return ", ".join(parts)

    def summarize_structured(self, changes: list[Change]) -> Intent:
        """Return a structured Intent object."""
        text = self.summarize(changes)
        categories = self._categorize(changes)
        areas = sorted({c.node.node_type for c in changes})
        confidence = min(1.0, max(0.1, len(changes) / 10))
        dominant = max(categories, key=lambda k: len(categories[k]), default="mixed")
        return Intent(
            category=dominant,
            description=text,
            affected_areas=areas,
            confidence=confidence,
        )

    def _categorize(self, changes: list[Change]) -> dict[str, list[Change]]:
        buckets: dict[str, list[Change]] = {}
        for c in changes:
            cat = self._detect_category(c)
            buckets.setdefault(cat, []).append(c)
        return buckets

    def _detect_category(self, change: Change) -> str:
        text = (change.details + " " + change.node.name).lower()
        for hint, cat in self.CATEGORY_HINTS.items():
            if hint in text:
                return cat
        if change.change_type == ChangeType.ADDED:
            return "feature"
        if change.change_type == ChangeType.REMOVED:
            return "chore"
        if change.change_type in (ChangeType.REFACTORED, ChangeType.RENAMED):
            return "refactor"
        return "fix"

    def _action_for_category(self, category: str) -> str:
        return {
            "feature": "Added",
            "chore": "Removed",
            "refactor": "Refactored",
            "fix": "Fixed",
            "security": "Secured",
        }.get(category, "Changed")

    def _pretty_list(self, items: list[str]) -> str:
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f" and {items[-1]}"
