# `mcp_server.py` — MCP Server

What this file does: exposes two tools over the Model Context Protocol (stdio transport): `diff_ast` (compute an AST-based diff) and `analyze_intent` (extract human-readable intent).

## Dependency map

- Optional runtime dep: `mcp[cli]>=1.2` (install via `pip install 'sin-code-ibd[mcp]'`).
- Imports: `.ast_diff.ASTDiffer`, `.intent.IntentAnalyzer` — both NOT defined in this package (see Caveats).
- Imported by: external MCP clients (stdio transport).

## Tools exposed

| Tool             | Inputs                                  | Returns                |
|------------------|-----------------------------------------|------------------------|
| `diff_ast`       | `old_code: str, new_code: str`          | JSON diff result       |
| `analyze_intent` | `diff: str`                              | JSON intent analysis   |

## Important config / limits

- **Transport: stdio.** JSON-RPC on stdin, JSON-RPC on stdout.
- **Optional dep.** `FastMCP` is imported lazily; the rest of the package works without it. `main()` raises `RuntimeError` if missing.
- **No state between calls.** Each tool invocation constructs a fresh `ASTDiffer` / `IntentAnalyzer`.

## Caveats / footguns

- **Known bug (pre-existing).** The tool bodies reference `ASTDiffer` and `IntentAnalyzer`, but the actual public classes are `ASTDiff` and `IntentSummarizer`. The module fails at runtime when a tool is called. This is a pre-existing bug; this doc does not fix it.
- **No authentication.** Anyone with stdio access to the process can call the tools. Run in a trusted environment.
- **Tool calls can be long** for large diffs. Configure your MCP client with a generous request timeout.

## Usage

```bash
# 1. Install with MCP support
pip install 'sin-code-ibd[mcp]'

# 2. Start the server (stdio transport)
python -m sin_code_ibd.mcp_server
```

Until the `ASTDiffer` / `IntentAnalyzer` bug is fixed, the tools will raise on call.
