# SIN-Code Intent-Based Diffing (IBD)

Generates semantic diffs that summarize architectural impact instead of just counting lines.

## Features
- AST-based diffing (symbol-level, not line-level)
- Intent classification (API change, refactor, feature, cleanup)
- Risk scoring with severity levels
- Git integration for uncommitted changes review
- Rich CLI output

## Install
```bash
pip install -e .
```

## Usage
```bash
ibd diff file_a.py file_b.py           # compare two files
ibd diff file_a.py file_b.py --json   # JSON output
ibd review-git                          # review uncommitted changes
```

## Architecture
- `ASTDiff`: Parses files with tree-sitter and compares symbol snapshots
- `IntentSummarizer`: Groups changes into architectural intents
- `RiskScorer`: Weighted scoring based on change type severity
