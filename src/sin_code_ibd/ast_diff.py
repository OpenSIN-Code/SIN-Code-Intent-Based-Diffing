"""AST-basierter Diff, der Symbole statt Zeilen vergleicht."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from tree_sitter import Language, Parser


@dataclass
class SymbolSnapshot:
    name: str
    kind: str
    signature: str
    body: str
    decorators: list[str]
    docstring: Optional[str]

    @property
    def fqid(self) -> str:
        return f"{self.kind}:{self.name}"


@dataclass
class Change:
    change_type: str  # added, removed, modified, signature_changed, docstring_changed
    symbol: str
    file: str
    details: dict = field(default_factory=dict)
    severity: str = "info"  # info, low, medium, high, critical


class ASTDiff:
    """Vergleicht Code via AST statt Text."""

    def __init__(self):
        self._parsers: dict[str, Parser] = {}
        self._init_parsers()

    def _init_parsers(self):
        for lang in ("python",):
            try:
                mod = __import__(f"tree_sitter_{lang}", fromlist=["language"])
                self._parsers[lang] = Parser(Language(mod.language()))
            except Exception:
                pass

    def _extract_symbols(self, source: bytes, lang: str = "python") -> dict[str, SymbolSnapshot]:
        if lang not in self._parsers:
            return {}
        tree = self._parsers[lang].parse(source)
        symbols: dict[str, SymbolSnapshot] = {}
        stack = [tree.root_node]
        while stack:
            node = stack.pop()
            if node.type in ("function_definition", "class_definition"):
                name_node = next((c for c in node.children if c.type == "identifier"), None)
                name = name_node.text.decode("utf-8") if name_node else "<anon>"
                kind = "function" if node.type == "function_definition" else "class"
                # Parameters
                params_node = next((c for c in node.children if c.type == "parameters"), None)
                params = params_node.text.decode("utf-8") if params_node else "()"
                decorators = []
                parent = node.parent
                if parent and parent.type == "decorated_definition":
                    for c in parent.children:
                        if c.type == "decorator":
                            decorators.append(c.text.decode("utf-8"))
                # Body: alles außer decorators/name/params
                body_parts = []
                for c in node.children:
                    if c.type in ("identifier", "parameters", "decorator"):
                        continue
                    body_parts.append(c.text.decode("utf-8"))
                body = "".join(body_parts).strip()
                # Docstring
                doc = None
                for c in node.children:
                    if c.type == "block":
                        for sub in c.children:
                            if sub.type == "expression_statement":
                                text = sub.text.decode("utf-8").strip()
                                if text.startswith(('\"\"\"', "'''", '"', "'")):
                                    doc = text
                                break
                symbols[f"{kind}:{name}"] = SymbolSnapshot(
                    name=name, kind=kind,
                    signature=f"{name}{params}",
                    body=body, decorators=decorators, docstring=doc,
                )
            stack.extend(node.children)
        return symbols

    def diff_files(self, file_a: str, file_b: str) -> list[Change]:
        with open(file_a, "rb") as f:
            src_a = f.read()
        with open(file_b, "rb") as f:
            src_b = f.read()
        return self.diff_strings(src_a, src_b, file_a)

    def diff_strings(self, src_a: bytes, src_b: bytes, file_label: str = "<inline>") -> list[Change]:
        sa = self._extract_symbols(src_a)
        sb = self._extract_symbols(src_b)
        changes: list[Change] = []

        added = set(sb.keys()) - set(sa.keys())
        removed = set(sa.keys()) - set(sb.keys())
        common = set(sa.keys()) & set(sb.keys())

        for sym in added:
            changes.append(Change("added", sym, file_label))
        for sym in removed:
            changes.append(Change("removed", sym, file_label, severity="medium"))

        for sym in common:
            a = sa[sym]
            b = sb[sym]
            if a.signature != b.signature:
                changes.append(Change(
                    "signature_changed", sym, file_label,
                    details={"old": a.signature, "new": b.signature},
                    severity="high",
                ))
            if set(a.decorators) != set(b.decorators):
                changes.append(Change(
                    "decorators_changed", sym, file_label,
                    details={"old": a.decorators, "new": b.decorators},
                    severity="medium",
                ))
            if a.docstring != b.docstring:
                changes.append(Change("docstring_changed", sym, file_label, severity="info"))
            if a.body != b.body:
                changes.append(Change(
                    "body_changed", sym, file_label,
                    details={"old_len": len(a.body), "new_len": len(b.body)},
                    severity="low",
                ))
        return changes
