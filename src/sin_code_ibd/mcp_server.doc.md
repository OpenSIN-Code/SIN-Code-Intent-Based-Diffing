# `mcp_server.py` — MCP Server for IBD

What this file does: exposes IBD tools to AI agents via the Model Context Protocol.

## Dependencies

- Imported by: CLI (`ibd serve`), external MCP hosts
- Imports: `ast_diff` (ASTDiffer), `intent` (IntentAnalyzer)

## Tools

- `diff_ast(old_code, new_code)` — compute AST-based diff between two code snippets
- `analyze_intent(diff)` — analyze the intent behind a code diff

## Usage

```bash
python -m sin_code_ibd.mcp_server
```

Requires `pip install -e ".[mcp]"`.

## Notes

Uses `mcp.server.fastmcp.FastMCP` for tool registration.
