"""Core node types and enums for semantic diffing.

Docs: src/sin_code_ibd/nodes.doc.md
"""

from __future__ import annotations
import dataclasses
from enum import Enum, auto
from typing import Any


class ChangeType(Enum):
    """Semantic change categories (not text-level)."""
    ADDED = auto()
    REMOVED = auto()
    MODIFIED = auto()
    RENAMED = auto()
    REFACTORED = auto()


@dataclasses.dataclass(frozen=True, slots=True)
class DiffNode:
    """A node in the AST that changed."""
    node_type: str          # e.g. 'FunctionDef', 'ClassDef', 'Import'
    name: str               # Identifier (function name, class name, etc.)
    file_path: str
    start_line: int
    end_line: int
    body: str | None = None
    signature: str | None = None
    parent: str | None = None

    def to_dict(self) -> dict[str, Any]:
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


@dataclasses.dataclass(frozen=False, slots=True)
class Change:
    """A single semantic change between two versions."""
    change_type: ChangeType
    node: DiffNode
    before: DiffNode | None = None   # populated for MODIFIED/RENAMED/REFACTORED
    after: DiffNode | None = None    # populated for MODIFIED/RENAMED/REFACTORED
    details: str = ""                # human-readable summary

    def is_public(self) -> bool:
        """True if the changed node is part of the public API."""
        name = self.node.name
        if not name:
            return False
        # underscore prefix = private
        return not name.startswith("_")

    def loc_delta(self) -> int:
        """Approximate lines of code changed."""
        if self.after and self.before:
            return abs(self.after.end_line - self.after.start_line -
                       (self.before.end_line - self.before.start_line))
        if self.after:
            return self.after.end_line - self.after.start_line
        if self.before:
            return self.before.end_line - self.before.start_line
        return 0
