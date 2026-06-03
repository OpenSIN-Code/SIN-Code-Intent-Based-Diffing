"""Report formatting utilities.

Three static methods that render structured objects as text or JSON.
Designed for CLI / log output — not optimized for HTML or rich UI.

Docs: report.doc.md
"""
from __future__ import annotations
import json
from typing import Any

from .nodes import Change
from .risk import RiskReport
from .intent import Intent


# ── ReportFormatter ───────────────────────────────────────────────────
class ReportFormatter:
    """Format changes and risk reports into human-readable text or JSON.

    All methods are `@staticmethod` — the class is a namespace, not
    a stateful object.
    """

    @staticmethod
    def format_changes(changes: list[Change]) -> str:
        """Render a list of `Change` as a multi-line text report.

        One line per change: `[CHANGE_TYPE] NodeType Name` + file:line + details.
        """
        lines: list[str] = [f"Total changes: {len(changes)}", ""]
        for c in changes:
            lines.append(f"[{c.change_type.name}] {c.node.node_type} {c.node.name}")
            lines.append(f"  File: {c.node.file_path}:{c.node.start_line}-{c.node.end_line}")
            lines.append(f"  Details: {c.details}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def format_risk(report: RiskReport) -> str:
        """Render a `RiskReport` as a multi-line text report.

        Includes total risk, per-factor breakdown, contributing factors
        (with reasons), and the list of hot files.
        """
        lines: list[str] = [f"Total Risk: {report.total_risk}", ""]
        lines.append("Breakdown:")
        for factor, score in report.breakdown.items():
            lines.append(f"  {factor}: {score}")
        lines.append("")
        lines.append("Factors:")
        for f in report.factors:
            lines.append(f"  - {f['change']}: {f['reason']} (risk={f['risk']})")
        lines.append("")
        lines.append(f"Hot files: {', '.join(report.hot_files) if report.hot_files else 'None'}")
        return "\n".join(lines)

    @staticmethod
    def to_json(data: Any) -> str:
        """Serialize `data` to pretty JSON. Falls back to `str(o)` for unknown types."""
        return json.dumps(data, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o), indent=2)
