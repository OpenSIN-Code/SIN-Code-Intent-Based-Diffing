"""ASTDiff — semantic diffing engine.

Compares two files or directories at the AST level. Output is a list
of `Change` objects, each tagged with a `ChangeType` (ADDED / REMOVED /
MODIFIED / RENAMED / REFACTORED) — not just text diffs.

Docs: ast_diff.doc.md
"""
from __future__ import annotations
import difflib
import os
from pathlib import Path
from typing import Any

from .nodes import Change, ChangeType, DiffNode
from .parsers import get_parser


# ── ASTDiff ────────────────────────────────────────────────────────────
class ASTDiff:
    """Compare two files or directories at the AST level.

    The engine is parser-agnostic — it relies on the parser registry
    (`parsers.get_parser`) to produce a list of `DiffNode` from each
    side, then computes the diff. Heuristics for RENAMED / REFACTORED
    / MODIFIED are intentionally simple; the goal is "good enough
    signal" for review UI, not formal equivalence.
    """

    def __init__(self, parser: str = "auto"):
        """Construct with a parser selector. `'auto'` picks from the file extension."""
        self.parser = parser

    # ── Public entry points ─────────────────────────────────────────────
    def diff_files(self, path_a: str, path_b: str) -> list[Change]:
        """Diff two files. Returns a list of semantic `Change` objects.

        Args:
            path_a: Path to the "before" file.
            path_b: Path to the "after" file.

        Returns:
            List of `Change` objects, one per detected semantic difference.
        """
        # `self.parser` is currently always "auto"; the conditional is
        # future-proofing for explicit per-language overrides.
        parser_a = get_parser(path_a) if self.parser == "auto" else get_parser(path_a)
        parser_b = get_parser(path_b) if self.parser == "auto" else get_parser(path_b)
        nodes_a = [DiffNode(**d) for d in parser_a.parse_file(path_a)]
        nodes_b = [DiffNode(**d) for d in parser_b.parse_file(path_b)]
        return self._diff_nodes(nodes_a, nodes_b)

    def diff_dirs(self, dir_a: str, dir_b: str) -> list[Change]:
        """Recursively diff two directories (matched by relative path).

        Files present in only one side are reported as REMOVED/ADDED for
        every AST node they contain. Files present in both are diffed
        with `diff_files`.
        """
        changes: list[Change] = []
        files_a = {str(p.relative_to(dir_a)): p for p in Path(dir_a).rglob("*") if p.is_file()}
        files_b = {str(p.relative_to(dir_b)): p for p in Path(dir_b).rglob("*") if p.is_file()}
        all_files = set(files_a.keys()) | set(files_b.keys())
        for rel in sorted(all_files):
            a = files_a.get(rel)
            b = files_b.get(rel)
            if a and b:
                changes.extend(self.diff_files(str(a), str(b)))
            elif a and not b:
                # Entire file removed — emit one REMOVED change per AST node.
                parser = get_parser(str(a))
                for d in parser.parse_file(str(a)):
                    changes.append(Change(
                        change_type=ChangeType.REMOVED,
                        node=DiffNode(**d),
                        details=f"File {rel} removed",
                    ))
            elif b and not a:
                # Entire file added — emit one ADDED change per AST node.
                parser = get_parser(str(b))
                for d in parser.parse_file(str(b)):
                    changes.append(Change(
                        change_type=ChangeType.ADDED,
                        node=DiffNode(**d),
                        details=f"File {rel} added",
                    ))
        return changes

    # ── Internal: node-level diffing ────────────────────────────────────
    def _diff_nodes(self, nodes_a: list[DiffNode], nodes_b: list[DiffNode]) -> list[Change]:
        """Diff two lists of `DiffNode` keyed by name. Classifies each pair as ADDED/REMOVED/RENAMED/REFACTORED/MODIFIED.

        Order of classification checks matters: RENAMED first (most
        specific), then REFACTORED, then MODIFIED (catch-all).
        """
        changes: list[Change] = []
        by_name_a = {n.name: n for n in nodes_a}
        by_name_b = {n.name: n for n in nodes_b}
        all_names = set(by_name_a.keys()) | set(by_name_b.keys())
        for name in all_names:
            na = by_name_a.get(name)
            nb = by_name_b.get(name)
            if na and not nb:
                changes.append(Change(
                    change_type=ChangeType.REMOVED,
                    node=na,
                    before=na,
                    details=f"Removed {na.node_type} {name}",
                ))
            elif nb and not na:
                changes.append(Change(
                    change_type=ChangeType.ADDED,
                    node=nb,
                    after=nb,
                    details=f"Added {nb.node_type} {name}",
                ))
            elif na and nb:
                if self._is_renamed(na, nb):
                    changes.append(Change(
                        change_type=ChangeType.RENAMED,
                        node=nb,
                        before=na,
                        after=nb,
                        details=f"Renamed {na.node_type} {name}",
                    ))
                elif self._is_refactored(na, nb):
                    changes.append(Change(
                        change_type=ChangeType.REFACTORED,
                        node=nb,
                        before=na,
                        after=nb,
                        details=f"Refactored {na.node_type} {name}",
                    ))
                elif self._is_modified(na, nb):
                    changes.append(Change(
                        change_type=ChangeType.MODIFIED,
                        node=nb,
                        before=na,
                        after=nb,
                        details=f"Modified {na.node_type} {name}",
                    ))
        return changes

    def _is_renamed(self, a: DiffNode, b: DiffNode) -> bool:
        """True if the node moved to a different parent but kept the same body."""
        if a.parent != b.parent and a.body == b.body:
            return True
        return False

    def _is_refactored(self, a: DiffNode, b: DiffNode) -> bool:
        """True if body similarity is high but signature unchanged (refactor, not rewrite).

        Heuristic: both bodies must be >5 lines (refactoring is a
        substantial change), signature must be identical (otherwise
        it's a MODIFIED), and line-similarity between 30% and 100%
        (identical would just be a no-op; <30% is a rewrite).
        """
        if not a.body or not b.body:
            return False
        if a.signature != b.signature:
            return False
        # Refactoring usually involves substantial bodies (>5 lines)
        if len(a.body.splitlines()) < 5 or len(b.body.splitlines()) < 5:
            return False
        # Simple heuristic: >30% line similarity but not identical
        seq = difflib.SequenceMatcher(None, a.body, b.body)
        ratio = seq.ratio()
        return 0.3 < ratio < 1.0

    def _is_modified(self, a: DiffNode, b: DiffNode) -> bool:
        """True if signature or body changed (catch-all MODIFIED)."""
        if a.signature != b.signature:
            return True
        if a.body != b.body:
            return True
        return False
