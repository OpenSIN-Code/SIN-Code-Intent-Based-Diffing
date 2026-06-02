"""RiskScorer — assign risk to semantic changes.

Docs: src/sin_code_ibd/risk.doc.md
"""

from __future__ import annotations
import dataclasses
from typing import Any

from .nodes import Change, ChangeType


@dataclasses.dataclass(frozen=False, slots=True)
class RiskReport:
    """Risk assessment for a set of changes."""
    total_risk: float            # 0.0-1.0
    factors: list[dict[str, Any]]
    hot_files: list[str]
    breakdown: dict[str, float]


class RiskScorer:
    """Score risk based on semantic change characteristics."""

    SECURITY_KEYWORDS: set[str] = {"auth", "login", "password", "crypto", "encrypt", "payment", "billing", "token", "secret", "oauth"}

    def score(self, changes: list[Change]) -> RiskReport:
        """Returns {total_risk: 0.0-1.0, factors: [...], hot_files: [...]}"""
        if not changes:
            return RiskReport(total_risk=0.0, factors=[], hot_files=[], breakdown={})

        breakdown: dict[str, float] = {
            "signature_change": 0.0,
            "removed_public_api": 0.0,
            "large_change": 0.0,
            "high_fan_in": 0.0,
            "new_dependencies": 0.0,
            "security_sensitive": 0.0,
        }

        factors: list[dict[str, Any]] = []
        hot_files: set[str] = set()

        for c in changes:
            # 1. Signature changes
            if c.change_type == ChangeType.MODIFIED and c.before and c.after:
                if c.before.signature != c.after.signature:
                    breakdown["signature_change"] = max(breakdown["signature_change"], 0.7)
                    factors.append({"change": c.node.name, "reason": "Signature changed", "risk": 0.7})
                    hot_files.add(c.node.file_path)

            # 2. Removed public APIs
            if c.change_type == ChangeType.REMOVED and c.is_public():
                breakdown["removed_public_api"] = max(breakdown["removed_public_api"], 0.9)
                factors.append({"change": c.node.name, "reason": "Public API removed", "risk": 0.9})
                hot_files.add(c.node.file_path)

            # 3. Large changes
            delta = c.loc_delta()
            if delta > 100:
                breakdown["large_change"] = max(breakdown["large_change"], 0.6)
                factors.append({"change": c.node.name, "reason": f"Large change ({delta} LOC)", "risk": 0.6})
                hot_files.add(c.node.file_path)

            # 4. New dependencies (added imports)
            if c.change_type == ChangeType.ADDED and c.node.node_type in ("Import", "ImportFrom"):
                breakdown["new_dependencies"] = max(breakdown["new_dependencies"], 0.4)
                factors.append({"change": c.node.name, "reason": "New dependency introduced", "risk": 0.4})
                hot_files.add(c.node.file_path)

            # 6. Security-sensitive areas
            if self._is_security_sensitive(c):
                breakdown["security_sensitive"] = max(breakdown["security_sensitive"], 0.85)
                factors.append({"change": c.node.name, "reason": "Security-sensitive area touched", "risk": 0.85})
                hot_files.add(c.node.file_path)

        # 5. High fan-in (heuristic: count how many changes mention same file)
        file_counts: dict[str, int] = {}
        for c in changes:
            file_counts[c.node.file_path] = file_counts.get(c.node.file_path, 0) + 1
        for fp, count in file_counts.items():
            if count >= 3:
                breakdown["high_fan_in"] = max(breakdown["high_fan_in"], 0.5)
                factors.append({"change": fp, "reason": "High fan-in (many changes)", "risk": 0.5})
                hot_files.add(fp)

        total = max(breakdown.values()) * 0.6 + sum(breakdown.values()) / len(breakdown) * 0.4
        total = min(1.0, max(0.0, total))

        return RiskReport(
            total_risk=round(total, 3),
            factors=factors,
            hot_files=sorted(hot_files),
            breakdown={k: round(v, 3) for k, v in breakdown.items()},
        )

    def _is_security_sensitive(self, change: Change) -> bool:
        text = (change.node.name + " " + change.details).lower()
        return any(kw in text for kw in self.SECURITY_KEYWORDS)
