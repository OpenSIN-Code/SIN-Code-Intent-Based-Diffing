# `risk.py` — Risk Scoring Engine

What this file does: assigns risk scores to semantic changes based on signature changes, removed APIs, security keywords, and large deltas.

## Dependencies

- Imported by: `__init__.py`, tests, MCP server
- Imports: `nodes` (Change, ChangeType)

## Config / Thresholds

- Security keywords: `auth`, `login`, `password`, `crypto`, `encrypt`, `payment`, `billing`, `token`, `secret`, `oauth`
- Risk factors: signature_change (0.7), removed_public_api (0.9), large_change>100LOC (0.6), high_fan_in>=3 (0.5), new_dependencies (0.4), security_sensitive (0.85)

## Usage

```python
from sin_code_ibd import RiskScorer
risk = RiskScorer().score(changes)
print(risk.total_risk)
```

## Notes

Total risk is a weighted blend: `max(breakdown) * 0.6 + mean(breakdown) * 0.4`.
