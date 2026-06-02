"""Tests for RiskScorer."""

import pytest

from sin_code_ibd.risk import RiskScorer, RiskReport
from sin_code_ibd.nodes import Change, ChangeType, DiffNode


@pytest.fixture
def scorer():
    return RiskScorer()


class TestScore:
    def test_empty_changes(self, scorer):
        report = scorer.score([])
        assert isinstance(report, RiskReport)
        assert report.total_risk == 0.0
        assert report.factors == []
        assert report.hot_files == []

    def test_no_risk(self, scorer):
        changes = [
            Change(ChangeType.ADDED, DiffNode("FunctionDef", "_private", "f.py", 1, 2), after=DiffNode("FunctionDef", "_private", "f.py", 1, 2))
        ]
        report = scorer.score(changes)
        assert report.total_risk < 0.3

    def test_removed_public_api(self, scorer):
        changes = [
            Change(
                ChangeType.REMOVED,
                DiffNode("FunctionDef", "public_api", "api.py", 1, 2),
                before=DiffNode("FunctionDef", "public_api", "api.py", 1, 2),
            )
        ]
        report = scorer.score(changes)
        assert report.total_risk >= 0.5
        assert any("Public API removed" in f["reason"] for f in report.factors)
        assert "api.py" in report.hot_files

    def test_signature_change(self, scorer):
        before = DiffNode("FunctionDef", "foo", "api.py", 1, 2, signature="def foo(a)")
        after = DiffNode("FunctionDef", "foo", "api.py", 1, 2, signature="def foo(a, b)")
        changes = [
            Change(ChangeType.MODIFIED, after, before=before, after=after)
        ]
        report = scorer.score(changes)
        assert report.total_risk >= 0.4
        assert any("Signature changed" in f["reason"] for f in report.factors)

    def test_large_change(self, scorer):
        body = "\n".join(["    x = 1"] * 150)
        before = DiffNode("FunctionDef", "big", "mod.py", 1, 2, body="def big(): pass")
        after = DiffNode("FunctionDef", "big", "mod.py", 1, 155, body=f"def big():\n{body}")
        changes = [
            Change(ChangeType.MODIFIED, after, before=before, after=after)
        ]
        report = scorer.score(changes)
        assert any("Large change" in f["reason"] for f in report.factors)
        assert "mod.py" in report.hot_files

    def test_new_dependency(self, scorer):
        changes = [
            Change(
                ChangeType.ADDED,
                DiffNode("Import", "requests", "requirements.py", 1, 1),
                after=DiffNode("Import", "requests", "requirements.py", 1, 1),
            )
        ]
        report = scorer.score(changes)
        assert any("New dependency" in f["reason"] for f in report.factors)

    def test_security_sensitive(self, scorer):
        changes = [
            Change(
                ChangeType.MODIFIED,
                DiffNode("FunctionDef", "encrypt_token", "crypto.py", 1, 2),
                before=DiffNode("FunctionDef", "encrypt_token", "crypto.py", 1, 2),
                after=DiffNode("FunctionDef", "encrypt_token", "crypto.py", 1, 2),
            )
        ]
        report = scorer.score(changes)
        assert any("Security-sensitive" in f["reason"] for f in report.factors)
        assert "crypto.py" in report.hot_files

    def test_high_fan_in(self, scorer):
        changes = [
            Change(ChangeType.MODIFIED, DiffNode("FunctionDef", f"fn{i}", "hot.py", i, i+1))
            for i in range(5)
        ]
        report = scorer.score(changes)
        assert any("High fan-in" in f["reason"] for f in report.factors)
        assert "hot.py" in report.hot_files

    def test_combined_risk(self, scorer):
        changes = [
            Change(ChangeType.REMOVED, DiffNode("FunctionDef", "public_api", "api.py", 1, 2), before=DiffNode("FunctionDef", "public_api", "api.py", 1, 2)),
            Change(ChangeType.MODIFIED, DiffNode("FunctionDef", "login", "auth.py", 1, 2), before=DiffNode("FunctionDef", "login", "auth.py", 1, 2, signature="def login()"), after=DiffNode("FunctionDef", "login", "auth.py", 1, 2, signature="def login(mfa)")),
        ]
        report = scorer.score(changes)
        assert report.total_risk >= 0.5
        assert len(report.factors) >= 2
        assert "api.py" in report.hot_files
        assert "auth.py" in report.hot_files

    def test_breakdown_values(self, scorer):
        changes = [
            Change(ChangeType.REMOVED, DiffNode("FunctionDef", "api", "api.py", 1, 2), before=DiffNode("FunctionDef", "api", "api.py", 1, 2)),
        ]
        report = scorer.score(changes)
        assert "removed_public_api" in report.breakdown
        assert "signature_change" in report.breakdown
        assert "security_sensitive" in report.breakdown
        assert all(0.0 <= v <= 1.0 for v in report.breakdown.values())

    def test_risk_bounds(self, scorer):
        changes = [
            Change(ChangeType.REMOVED, DiffNode("FunctionDef", "api", "api.py", 1, 2), before=DiffNode("FunctionDef", "api", "api.py", 1, 2)),
            Change(ChangeType.MODIFIED, DiffNode("FunctionDef", "login", "auth.py", 1, 2), before=DiffNode("FunctionDef", "login", "auth.py", 1, 2, signature="def login()"), after=DiffNode("FunctionDef", "login", "auth.py", 1, 2, signature="def login(mfa)")),
            Change(ChangeType.ADDED, DiffNode("Import", "new_lib", "deps.py", 1, 1), after=DiffNode("Import", "new_lib", "deps.py", 1, 1)),
        ]
        report = scorer.score(changes)
        assert 0.0 <= report.total_risk <= 1.0
