"""JavaScript parser — tree-sitter when available, regex fallback.

Tries `tree-sitter` + `tree-sitter-javascript` first. If the import
fails or the parse throws, falls back to a `(?:function|class) NAME`
regex that captures only the declaration line (no body).

Docs: js_parser.doc.md
"""
from __future__ import annotations
from pathlib import Path
from typing import Any


# ── JSParser ──────────────────────────────────────────────────────────
class JSParser:
    """Extract AST nodes from JavaScript source.

    Two implementations under one class:
      - `_tree_sitter_parse` (preferred) — full AST, captures body & signature
      - `_regex_parse` (fallback) — captures only the line of the declaration
    """

    def parse_file(self, path: str) -> list[dict[str, Any]]:
        """Read `path` and parse; returns the standard `DiffNode` dict list."""
        source = Path(path).read_text(encoding="utf-8")
        return self.parse_source(source, file_path=path)

    def parse_source(self, source: str, file_path: str = "") -> list[dict[str, Any]]:
        """Parse `source` (a string); returns the standard `DiffNode` dict list.

        Tries tree-sitter first, falls back to regex on any error.
        """
        try:
            return self._tree_sitter_parse(source, file_path)
        except Exception:
            return self._regex_parse(source, file_path)

    # ── Internal: tree-sitter path ──────────────────────────────────────
    def _tree_sitter_parse(self, source: str, file_path: str) -> list[dict[str, Any]]:
        from tree_sitter import Language, Parser  # type: ignore
        import tree_sitter_javascript as js  # type: ignore
        lang = Language(js.language(), "javascript")
        parser = Parser()
        parser.set_language(lang)
        tree = parser.parse(bytes(source, "utf-8"))
        return self._extract_nodes(tree.root_node, file_path, source)

    def _extract_nodes(self, node, file_path: str, source: str) -> list[dict[str, Any]]:
        """Recursive tree-sitter walker; collects function/method/class nodes."""
        nodes: list[dict[str, Any]] = []
        cursor = node.walk()
        if cursor.node.type in ("function_declaration", "method_definition", "class_declaration"):
            name = ""
            for child in cursor.node.children:
                if child.type == "identifier":
                    name = source[child.start_byte:child.end_byte]
                    break
            nodes.append({
                "node_type": cursor.node.type,
                "name": name,
                "file_path": file_path,
                "start_line": cursor.node.start_point[0] + 1,
                "end_line": cursor.node.end_point[0] + 1,
                "body": source[cursor.node.start_byte:cursor.node.end_byte],
                "signature": None,
                "parent": "",
            })
        for child in cursor.node.children:
            nodes.extend(self._extract_nodes(child, file_path, source))
        return nodes

    # ── Internal: regex fallback ────────────────────────────────────────
    def _regex_parse(self, source: str, file_path: str) -> list[dict[str, Any]]:
        """Regex fallback when tree-sitter is unavailable.

        Captures only the line of the declaration (no body, no signature).
        `start_line == end_line` for every node.
        """
        import re
        nodes: list[dict[str, Any]] = []
        # Simple function / class regex
        for m in re.finditer(r"(?:function|class)\s+(\w+)", source):
            line = source[:m.start()].count("\n") + 1
            nodes.append({
                "node_type": "function_declaration" if m.group(0).startswith("function") else "class_declaration",
                "name": m.group(1),
                "file_path": file_path,
                "start_line": line,
                "end_line": line,
                "body": None,
                "signature": None,
                "parent": "",
            })
        return nodes
