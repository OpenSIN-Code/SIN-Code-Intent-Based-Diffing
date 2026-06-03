"""SIN-Code-Intent-Based-Diffing — AST-based semantic diffing with intent and risk analysis.

Re-exports the public API: `ASTDiff` (the diffing engine),
`IntentSummarizer` (human-readable summaries), `RiskScorer` (numeric
risk assessment), and the data classes `DiffNode`, `Change`, and
`ChangeType`. See `ast_diff.doc.md` for the engine and `intent.doc.md`
/ `risk.doc.md` for the analyses.

Docs: __init__.doc.md
"""

from .ast_diff import ASTDiff
from .intent import IntentSummarizer
from .risk import RiskScorer, RiskReport
from .nodes import DiffNode, ChangeType, Change

__all__ = [
    "ASTDiff",
    "IntentSummarizer",
    "RiskScorer",
    "RiskReport",
    "DiffNode",
    "ChangeType",
    "Change",
]
