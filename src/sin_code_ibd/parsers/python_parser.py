"""Python parser using the stdlib `ast` module.

Pure-stdlib implementation — no external dependency. Captures
functions, async functions, classes, and imports. Body and signature
are extracted for functions and classes; imports are recorded as a
single line.

Docs: python_parser.doc.md
"""
from __future__ import annotations
import ast
import inspect
from pathlib import Path
from typing import Any


# ── PythonParser ──────────────────────────────────────────────────────
class PythonParser:
    """Extract AST nodes from Python source code.

    Produces one dict per `FunctionDef` / `AsyncFunctionDef` / `ClassDef`
    / `Import` / `ImportFrom`. Results are sorted by `start_line` for
    stable downstream diffing.
    """

    def parse_file(self, path: str) -> list[dict[str, Any]]:
        """Read `path` and parse; returns the standard `DiffNode` dict list."""
        source = Path(path).read_text(encoding="utf-8")
        return self.parse_source(source, file_path=path)

    def parse_source(self, source: str, file_path: str = "") -> list[dict[str, Any]]:
        """Parse `source` (a string) and walk the AST.

        Raises:
            SyntaxError: if the source doesn't parse (caller's job to catch).
        """
        tree = ast.parse(source)
        nodes: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                nodes.append(self._node_to_dict(node, source, file_path))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                nodes.append(self._import_to_dict(node, source, file_path))
        # Sort by start line for stable ordering
        nodes.sort(key=lambda n: n["start_line"])
        return nodes

    # ── Internal: dict conversion ──────────────────────────────────────
    def _node_to_dict(self, node: ast.AST, source: str, file_path: str) -> dict[str, Any]:
        """Convert a function/class AST node to a `DiffNode` dict."""
        name = getattr(node, "name", "")
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start)
        parent = getattr(node, "parent", None)
        parent_name = ""
        # The `parent` attribute is set by `ast.parse` only on Python 3.12+;
        # on older versions it's None and we leave `parent_name` empty.
        if parent and isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            parent_name = parent.name
        body = self._extract_body(node, source)
        signature = self._extract_signature(node, source)
        return {
            "node_type": type(node).__name__,
            "name": name,
            "file_path": file_path,
            "start_line": start,
            "end_line": end,
            "body": body,
            "signature": signature,
            "parent": parent_name,
        }

    def _import_to_dict(self, node: ast.AST, source: str, file_path: str) -> dict[str, Any]:
        """Convert an `Import` or `ImportFrom` AST node to a `DiffNode` dict.

        `name` is set to a comma-separated list of imported names
        (with the module prefix for `ImportFrom`).
        """
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start)
        if isinstance(node, ast.Import):
            names = ", ".join(alias.name for alias in node.names)
        else:
            module = node.module or ""
            names = f"{module}: " + ", ".join(alias.name for alias in node.names)
        return {
            "node_type": type(node).__name__,
            "name": names,
            "file_path": file_path,
            "start_line": start,
            "end_line": end,
            "body": None,
            "signature": None,
            "parent": "",
        }

    def _extract_body(self, node: ast.AST, source: str) -> str:
        """Slice the source from `lineno` to `end_lineno` (1-based, inclusive)."""
        lines = source.splitlines()
        start = getattr(node, "lineno", 1) - 1
        end = getattr(node, "end_lineno", start + 1)
        return "\n".join(lines[start:end])

    def _extract_signature(self, node: ast.AST, source: str) -> str:
        """Render a `def f(x, y)` / `class C(Base)` form.

        Falls back to `"..."` for args on Python < 3.9 (no `ast.unparse`).
        """
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ast.unparse(node.args) if hasattr(ast, "unparse") else "..."
            return f"def {node.name}({args})"
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases] if hasattr(ast, "unparse") else []
            base_str = "(" + ", ".join(bases) + ")" if bases else ""
            return f"class {node.name}{base_str}"
        return ""
