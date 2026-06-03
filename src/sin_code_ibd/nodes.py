"""Core node types and enums for semantic diffing.

Three data classes: `ChangeType` (enum), `DiffNode` (an AST node from
one side of a diff), and `Change` (a delta between two nodes or an
add/remove).

Docs: nodes.doc.md
"""
from __future__ import annotations
import dataclasses
from enum import Enum, auto
from typing import Any


# ── ChangeType enum ───────────────────────────────────────────────────
class ChangeType(Enum):
    """Semantic change categories (not text-level).

    - `ADDED`: node exists only in the "after" side
    - `REMOVED`: node exists only in the "before" side
    - `MODIFIED`: same node, signature or body changed
    - `RENAMED`: same body, parent changed
    - `REFACTORED`: same signature, body substantially rewritten
    """
    ADDED = auto()
    REMOVED = auto()
    MODIFIED = auto()
    RENAMED = auto()
    REFACTORED = auto()


# ── DiffNode ──────────────────────────────────────────────────────────
@dataclasses.dataclass(frozen=True, slots=True)
class DiffNode:
    """A node in the AST that changed.

    `frozen=True` + `slots=True` = immutable + memory-efficient.

    Fields:
      - `node_type`: AST class name (`FunctionDef`, `ClassDef`, `Import`, …)
      - `name`: identifier (function/class/import name)
      - `file_path`: absolute or relative path
      - `start_line` / `end_line`: 1-based, inclusive
      - `body`: source text (None for imports and for regex-parsed JS/TS)
      - `signature`: rendered `def f(x, y)` / `class C(Base)` form
      - `parent`: parent symbol name (for nested functions/classes)
    """
    node_type: str
    name: str
    file_path: str
    start_line: int
    end_line: int
    body: str | None = None
    signature: str | None = None
    parent: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable view (all fields, no transformation)."""
        return {
            "node_type": self.node_type,
            "name": self.name,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "body": self.body,
            "signature": self.signature,
            "parent": self.parent,
        }


# ── Change ────────────────────────────────────────────────────────────
@dataclasses.dataclass(frozen=False, slots=True)
class Change:
    """A single semantic change between two versions.

    Mutable (frozen=False) so callers can post-process if needed.
    `before` and `after` are populated only for MODIFIED / RENAMED /
    REFACTORED; ADDED has only `after`; REMOVED has only `before`.
    """
    change_type: ChangeType
    node: DiffNode
    before: DiffNode | None = None
    after: DiffNode | None = None
    details: str = ""

    def is_public(self) -> bool:
        """True if the changed node is part of the public API (no leading underscore)."""
        name = self.node.name
        if not name:
            return False
        # Underscore prefix = private (Python convention).
        return not name.startswith("_")

    def loc_delta(self) -> int:
        """Approximate lines of code changed.

        Returns 0 when no before/after is set. Otherwise returns the
        size of the node (or the absolute delta between sides for
        MODIFIED).
        """
        if self.after and self.before:
            return abs(self.after.end_line - self.after.start_line -
                       (self.before.end_line - self.before.start_line))
        if self.after:
            return self.after.end_line - self.after.start_line
        if self.before:
            return self.before.end_line - self.before.start_line
        return 0
