"""Parsers package — auto-detect language from file extension.

Docs: src/sin_code_ibd/parsers/__init__.doc.md
"""

from __future__ import annotations
from typing import Protocol

from .python_parser import PythonParser
from .js_parser import JSParser
from .ts_parser import TSParser


class ParserProtocol(Protocol):
    """Shared interface for all language parsers."""
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


def get_parser(path: str) -> ParserProtocol:
    """Return a parser instance based on the file extension."""
    from pathlib import Path
    ext = Path(path).suffix.lower()
    cls = PARSER_REGISTRY.get(ext, PythonParser)
    return cls()

__all__ = ["PythonParser", "JSParser", "TSParser", "get_parser", "PARSER_REGISTRY"]
