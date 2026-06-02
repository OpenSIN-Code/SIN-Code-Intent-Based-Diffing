# Installation — `sin-code-ibd`

## Requirements

- Python **3.10+**
- `pip` (or `uv`/`pipx`)
- Git (for repository-aware features)

## Install from source (recommended during preview)

```bash
git clone https://github.com/OpenSIN-Code/SIN-Code-Intent-Based-Diffing.git
cd SIN-Code-Intent-Based-Diffing
pip install -e .
```

This installs the importable package `sin_code_ibd`.

## Install into an isolated environment

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e .
```

## Optional: JS/TS support

For JavaScript/TypeScript parsing, install the optional `js` extra:

```bash
pip install -e ".[js]"
```

## Optional: MCP server support

The MCP server requires the optional `mcp` dependency:

```bash
pip install -e ".[mcp]"
```

## Verify the installation

```bash
pytest -q
python -c "from sin_code_ibd import ASTDiff, IntentSummarizer, RiskScorer; print('OK')"
```

## Uninstall

```bash
pip uninstall sin-code-ibd
```
