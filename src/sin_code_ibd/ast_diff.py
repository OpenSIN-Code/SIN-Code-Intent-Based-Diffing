"""ASTDiff — semantic diffing engine.

Docs: src/sin_code_ibd/ast_diff.py.doc.md
"""

from __future__ import annotations
import difflib
import os
from pathlib import Path
from typing import Any

from .nodes import Change, ChangeType, DiffNode
from .parsers import get_parser


class ASTDiff:
    """Compare two files or directories at the AST level."""

    def __init__(self, parser: str = "auto"):
        """parser='auto' detects from file extension."""
        self.parser = parser

    def diff_files(self, path_a: str, path_b: str) -> list[Change]:
        """Returns list of semantic changes (not just text diffs)."""
        parser_a = get_parser(path_a) if self.parser == "auto" else get_parser(path_a)
        parser_b = get_parser(path_b) if self.parser == "auto" else get_parser(path_b)
        nodes_a = [DiffNode(**d) for d in parser_a.parse_file(path_a)]
        nodes_b = [DiffNode(**d) for d in parser_b.parse_file(path_b)]
        return self._diff_nodes(nodes_a, nodes_b)

    def diff_dirs(self, dir_a: str, dir_b: str) -> list[Change]:
        """Recursively diff two directories."""
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
                # Entire file removed
                parser = get_parser(str(a))
                for d in parser.parse_file(str(a)):
                    changes.append(Change(
                        change_type=ChangeType.REMOVED,
                        node=DiffNode(**d),
                        details=f"File {rel} removed",
                    ))
            elif b and not a:
                # Entire file added
                parser = get_parser(str(b))
                for d in parser.parse_file(str(b)):
                    changes.append(Change(
                        change_type=ChangeType.ADDED,
                        node=DiffNode(**d),
                        details=f"File {rel} added",
                    ))
        return changes

    def _diff_nodes(self, nodes_a: list[DiffNode], nodes_b: list[DiffNode]) -> list[Change]:
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
        """True if the node moved to a different parent but kept body."""
        if a.parent != b.parent and a.body == b.body:
            return True
        return False

    def _is_refactored(self, a: DiffNode, b: DiffNode) -> bool:
        """True if body similarity is high but structure changed, signature unchanged."""
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
        """True if signature or body changed."""
        if a.signature != b.signature:
            return True
        if a.body != b.body:
            return True
        return False
