"""Parsers package — auto-detect language from file extension.

The package exposes three parser classes (`PythonParser`, `JSParser`,
`TSParser`), a `ParserProtocol` (typing-only interface), a
`PARSER_REGISTRY` (extension → class), and a `get_parser(path)`
factory. Unknown extensions fall back to `PythonParser`.

Docs: __init__.doc.md
"""
from __future__ import annotations
from typing import Protocol

from .python_parser import PythonParser
from .js_parser import JSParser
from .ts_parser import TSParser


# ── ParserProtocol ────────────────────────────────────────────────────
class ParserProtocol(Protocol):
    """Shared interface for all language parsers.

    Implementations MUST expose `parse_file(path)` and
    `parse_source(source, file_path="")`, both returning a list of
    `dict`s with the keys consumed by `DiffNode(**d)`.
    """
    def parse_file(self, path: str) -> list[dict]: ...
    def parse_source(self, source: str, file_path: str = "") -> list[dict]: ...


# Registry mapping extension -> parser class
PARSER_REGISTRY: dict[str, type[ParserProtocol]] = {
    ".py": PythonParser,
    ".js": JSParser,
    ".jsx": JSParser,
    ".ts": TSParser,
    ".tsx": TSParser,
}


# ── Factory ──────────────────────────────────────────────────────────
def get_parser(path: str) -> ParserProtocol:
    """Return a parser instance based on the file extension.

    Args:
        path: File path (the extension is what matters; the file
              doesn't need to exist).

    Returns:
        A fresh parser instance. Unknown extensions fall back to
        `PythonParser` so a misconfigured registry degrades gracefully.
    """
    from pathlib import Path
    ext = Path(path).suffix.lower()
    cls = PARSER_REGISTRY.get(ext, PythonParser)
    return cls()

__all__ = ["PythonParser", "JSParser", "TSParser", "get_parser", "PARSER_REGISTRY"]
