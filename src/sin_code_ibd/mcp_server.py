"""MCP server for agent integration.

Exposes two tools over the Model Context Protocol (stdio transport):
`diff_ast` (compute an AST-based diff) and `analyze_intent` (extract
human-readable intent).

Docs: mcp_server.doc.md
"""
from __future__ import annotations

import json

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    # Optional dep — the rest of the package works without it.
    FastMCP = None

from .ast_diff import ASTDiffer
from .intent import IntentAnalyzer


def main():
    """Start the MCP server over stdio (blocking).

    Raises:
        RuntimeError: if the `mcp` extra is not installed.
    """
    if FastMCP is None:
        raise RuntimeError("mcp package not installed. Install with: pip install 'sin-code-ibd[mcp]'")

    mcp = FastMCP("sin-code-ibd")

    @mcp.tool()
    def diff_ast(old_code: str, new_code: str) -> str:
        """Compute AST-based diff between two code snippets.

        Args:
            old_code: The "before" source.
            new_code: The "after" source.

        Returns:
            JSON string with the diff result.
        """
        differ = ASTDiffer()
        return json.dumps(differ.diff(old_code, new_code), indent=2)

    @mcp.tool()
    def analyze_intent(diff: str) -> str:
        """Analyze the intent behind a code diff.

        Args:
            diff: Diff text (typically from `diff_ast`).

        Returns:
            JSON string with the intent analysis.
        """
        analyzer = IntentAnalyzer()
        return json.dumps(analyzer.analyze(diff), indent=2)

    mcp.run()


if __name__ == "__main__":
    main()
