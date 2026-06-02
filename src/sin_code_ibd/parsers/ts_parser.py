"""TypeScript parser (stub — tree-sitter optional).

Docs: src/sin_code_ibd/parsers/ts_parser.doc.md
"""

from __future__ import annotations
from pathlib import Path
from typing import Any


class TSParser:
    """Extract AST nodes from TypeScript source.
    Falls back to regex-based heuristic if tree-sitter is unavailable."""

    def parse_file(self, path: str) -> list[dict[str, Any]]:
        source = Path(path).read_text(encoding="utf-8")
        return self.parse_source(source, file_path=path)

    def parse_source(self, source: str, file_path: str = "") -> list[dict[str, Any]]:
        try:
            return self._tree_sitter_parse(source, file_path)
        except Exception:
            return self._regex_parse(source, file_path)

    def _tree_sitter_parse(self, source: str, file_path: str) -> list[dict[str, Any]]:
        from tree_sitter import Language, Parser  # type: ignore
        import tree_sitter_typescript as ts  # type: ignore
        lang = Language(ts.language_tsx() if file_path.endswith(".tsx") else ts.language_typescript(), "typescript")
        parser = Parser()
        parser.set_language(lang)
        tree = parser.parse(bytes(source, "utf-8"))
        return self._extract_nodes(tree.root_node, file_path, source)

    def _extract_nodes(self, node, file_path: str, source: str) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        cursor = node.walk()
        if cursor.node.type in ("function_declaration", "method_definition", "class_declaration", "interface_declaration"):
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

    def _regex_parse(self, source: str, file_path: str) -> list[dict[str, Any]]:
        import re
        nodes: list[dict[str, Any]] = []
        for m in re.finditer(r"(?:function|class|interface)\s+(\w+)", source):
            line = source[:m.start()].count("\n") + 1
            nodes.append({
                "node_type": "function_declaration" if m.group(0).startswith("function") else "class_declaration" if m.group(0).startswith("class") else "interface_declaration",
                "name": m.group(1),
                "file_path": file_path,
                "start_line": line,
                "end_line": line,
                "body": None,
                "signature": None,
                "parent": "",
            })
        return nodes
