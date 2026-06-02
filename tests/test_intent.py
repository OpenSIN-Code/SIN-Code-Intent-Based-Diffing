"""Tests for IntentSummarizer."""

import pytest

from sin_code_ibd.intent import IntentSummarizer, Intent
from sin_code_ibd.nodes import Change, ChangeType, DiffNode


@pytest.fixture
def summarizer():
    return IntentSummarizer()


class TestSummarize:
    def test_empty_changes(self, summarizer):
        assert summarizer.summarize([]) == "No semantic changes detected."

    def test_simple_addition(self, summarizer):
        changes = [
            Change(
                change_type=ChangeType.ADDED,
                node=DiffNode("FunctionDef", "new_feature", "f.py", 1, 2),
                after=DiffNode("FunctionDef", "new_feature", "f.py", 1, 2),
            )
        ]
        text = summarizer.summarize(changes)
        assert "Added" in text
        assert "new_feature" in text

    def test_simple_removal(self, summarizer):
        changes = [
            Change(
                change_type=ChangeType.REMOVED,
                node=DiffNode("FunctionDef", "old_feature", "f.py", 1, 2),
                before=DiffNode("FunctionDef", "old_feature", "f.py", 1, 2),
            )
        ]
        text = summarizer.summarize(changes)
        assert "Removed" in text
        assert "old_feature" in text

    def test_refactor(self, summarizer):
        changes = [
            Change(
                change_type=ChangeType.REFACTORED,
                node=DiffNode("FunctionDef", "extract_method", "f.py", 1, 2),
                before=DiffNode("FunctionDef", "extract_method", "f.py", 1, 2),
                after=DiffNode("FunctionDef", "extract_method", "f.py", 1, 2),
                details="Refactored extract_method",
            )
        ]
        text = summarizer.summarize(changes)
        assert "Refactored" in text

    def test_mixed_changes(self, summarizer):
        changes = [
            Change(ChangeType.ADDED, DiffNode("FunctionDef", "foo", "f.py", 1, 2), after=DiffNode("FunctionDef", "foo", "f.py", 1, 2)),
            Change(ChangeType.REMOVED, DiffNode("FunctionDef", "bar", "f.py", 3, 4), before=DiffNode("FunctionDef", "bar", "f.py", 3, 4)),
        ]
        text = summarizer.summarize(changes)
        assert "Added" in text or "Removed" in text

    def test_security_hint(self, summarizer):
        changes = [
            Change(
                ChangeType.MODIFIED,
                DiffNode("FunctionDef", "login", "auth.py", 1, 2),
                before=DiffNode("FunctionDef", "login", "auth.py", 1, 2),
                after=DiffNode("FunctionDef", "login", "auth.py", 1, 2),
                details="Fixed login flow",
            )
        ]
        text = summarizer.summarize(changes)
        assert "login" in text


class TestStructured:
    def test_structured_intent(self, summarizer):
        changes = [
            Change(ChangeType.ADDED, DiffNode("ClassDef", "SSOProvider", "app.py", 1, 2), after=DiffNode("ClassDef", "SSOProvider", "app.py", 1, 2))
        ]
        intent = summarizer.summarize_structured(changes)
        assert isinstance(intent, Intent)
        assert intent.category == "feature"
        assert "SSOProvider" in intent.description
        assert "ClassDef" in intent.affected_areas
        assert 0.0 < intent.confidence <= 1.0

    def test_structured_confidence(self, summarizer):
        changes = [
            Change(ChangeType.ADDED, DiffNode("FunctionDef", f"fn{i}", "f.py", i, i+1), after=DiffNode("FunctionDef", f"fn{i}", "f.py", i, i+1))
            for i in range(15)
        ]
        intent = summarizer.summarize_structured(changes)
        assert intent.confidence == 1.0
