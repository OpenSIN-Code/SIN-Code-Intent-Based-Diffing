# SIN-Code Intent-Based Diffing (IBD)

> AST-based semantic diffing with intent summarization and risk scoring. Understands functions, classes, and imports — not just lines of text.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

Part of the [SIN-Code](https://github.com/OpenSIN-Code) agent-engineering stack. Install all subsystems together via the [SIN-Code Bundle](https://github.com/OpenSIN-Code/SIN-Code-Bundle).

## Features

- **Semantic diffs** — not text-based; understands functions, classes, imports, and renames
- **Intent detection** — auto-generates human-readable summaries like "Refactored auth flow, added OAuth support"
- **Risk scoring** — flags signature changes, removed public APIs, security-sensitive edits, and large changes
- **Structured output** — get `Intent` objects with category, confidence, and affected areas
- **Multi-language** — Python (stdlib `ast`), JS/TS via optional tree-sitter extras
- **MCP server** — expose diffing tools to AI agents via the Model Context Protocol

## Installation

```bash
pip install -e .
```

Optional JS/TS support:
```bash
pip install -e ".[js]"
```

Optional MCP server support:
```bash
pip install -e ".[mcp]"
```

See [INSTALL.md](./INSTALL.md) for detailed setup instructions.

## Usage

### Library

```python
from sin_code_ibd import ASTDiff, IntentSummarizer, RiskScorer

# Diff two files
changes = ASTDiff().diff_files("a.py", "b.py")

# Summarize intent
intent = IntentSummarizer().summarize(changes)
print(intent)
# "Refactored auth flow, added OAuth support"

# Score risk
risk = RiskScorer().score(changes)
print(risk.total_risk)      # 0.0–1.0
print(risk.hot_files)       # files that need careful review
print(risk.breakdown)       # per-factor risk scores

# Structured intent
structured = IntentSummarizer().summarize_structured(changes)
print(structured.category)         # 'feature', 'refactor', 'fix', ...
print(structured.confidence)       # 0.0–1.0
print(structured.affected_areas) # ['FunctionDef', 'ClassDef', ...]
```

### Diff directories

```python
changes = ASTDiff().diff_dirs("src_v1", "src_v2")
```

## Testing

```bash
pytest tests/ -v
```

## MCP Server

Run the MCP server for agent integration:

```bash
python -m sin_code_ibd.mcp_server
```

Tools exposed:
- `diff_ast(old_code, new_code)` — compute AST-based diff between two code snippets
- `analyze_intent(diff)` — analyze the intent behind a code diff

## Integration

IBD is designed to work as part of the SIN-Code ecosystem:

- **SIN-Code Bundle** — orchestrates all subsystems from a single CLI (`sin`)
- **Semantic Codebase Knowledge Graphs (SCKG)** — enrich diffs with graph context (fan-in, dependencies)
- **Verification Oracle** — trigger re-verification for high-risk changes
- **Review Interface** — feed diff output into human review workflows

## License

MIT — see [LICENSE](./LICENSE).
