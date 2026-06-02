"""Tests for node types and report formatting."""

import pytest

from sin_code_ibd.nodes import DiffNode, Change, ChangeType
from sin_code_ibd.report import ReportFormatter
from sin_code_ibd.risk import RiskReport


class TestDiffNode:
    def test_to_dict(self):
        node = DiffNode("FunctionDef", "foo", "f.py", 1, 2, body="def foo(): pass", signature="def foo()", parent="A")
        d = node.to_dict()
        assert d["node_type"] == "FunctionDef"
        assert d["name"] == "foo"
        assert d["body"] == "def foo(): pass"

    def test_public(self):
        public = Change(ChangeType.ADDED, DiffNode("FunctionDef", "public", "f.py", 1, 2))
        private = Change(ChangeType.ADDED, DiffNode("FunctionDef", "_private", "f.py", 1, 2))
        assert public.is_public()
        assert not private.is_public()

    def test_loc_delta(self):
        c = Change(
            ChangeType.MODIFIED,
            DiffNode("FunctionDef", "foo", "f.py", 1, 2),
            before=DiffNode("FunctionDef", "foo", "f.py", 1, 2),
            after=DiffNode("FunctionDef", "foo", "f.py", 1, 10),
        )
        assert c.loc_delta() == 8

    def test_loc_delta_added(self):
        c = Change(ChangeType.ADDED, DiffNode("FunctionDef", "foo", "f.py", 1, 5), after=DiffNode("FunctionDef", "foo", "f.py", 1, 5))
        assert c.loc_delta() == 4

    def test_loc_delta_removed(self):
        c = Change(ChangeType.REMOVED, DiffNode("FunctionDef", "foo", "f.py", 1, 5), before=DiffNode("FunctionDef", "foo", "f.py", 1, 5))
        assert c.loc_delta() == 4


class TestReportFormatter:
    def test_format_changes(self):
        changes = [
            Change(ChangeType.ADDED, DiffNode("FunctionDef", "foo", "f.py", 1, 2), after=DiffNode("FunctionDef", "foo", "f.py", 1, 2))
        ]
        text = ReportFormatter.format_changes(changes)
        assert "ADDED" in text
        assert "foo" in text

    def test_format_risk(self):
        report = RiskReport(
            total_risk=0.5,
            factors=[{"change": "foo", "reason": "Signature changed", "risk": 0.7}],
            hot_files=["f.py"],
            breakdown={"signature_change": 0.7}
        )
        text = ReportFormatter.format_risk(report)
        assert "0.5" in text
        assert "f.py" in text

    def test_to_json(self):
        changes = [
            Change(ChangeType.ADDED, DiffNode("FunctionDef", "foo", "f.py", 1, 2), after=DiffNode("FunctionDef", "foo", "f.py", 1, 2))
        ]
        json_str = ReportFormatter.to_json(changes)
        assert "ADDED" in json_str
        assert "foo" in json_str

    def test_empty_changes_format(self):
        text = ReportFormatter.format_changes([])
        assert "Total changes: 0" in text

    def test_empty_risk_format(self):
        report = RiskReport(total_risk=0.0, factors=[], hot_files=[], breakdown={})
        text = ReportFormatter.format_risk(report)
        assert "None" in text
