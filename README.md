# SIN-Code-Intent-Based-Diffing (IBD)

AST-based semantic diffing with intent summarization and risk scoring.

## Installation

```bash
pip install sin-code-ibd
```

## Quick Start

```python
from sin_code_ibd import ASTDiff, IntentSummarizer, RiskScorer

changes = ASTDiff().diff_files("a.py", "b.py")
intent = IntentSummarizer().summarize(changes)
risk = RiskScorer().score(changes)

print(intent)
print(risk.total_risk)
```

## Features

- **Semantic diffs** — not text-based; understands functions, classes, imports
- **Intent detection** — auto-generates human-readable summaries
- **Risk scoring** — flags signature changes, removed APIs, security-sensitive edits
- **Multi-language** — Python (stdlib `ast`), JS/TS (tree-sitter, optional)

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
