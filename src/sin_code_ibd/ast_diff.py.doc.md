# ast_diff.py

What does this file do? ASTDiff compares two files or directories at the AST level, producing semantic changes (Added, Removed, Modified, Renamed, Refactored) rather than text-level diffs.

Which other files import / touch it? `__init__.py` exports ASTDiff. Tests in `tests/test_ast_diff.py` cover it.

Important config values & limits: None hardcoded; large-change threshold is in RiskScorer (>100 LOC).

Why certain decisions were made: Uses name-based matching for functions/classes. Rename detection requires identical body but different file/parent. Refactor detection uses SequenceMatcher ratio >0.3 and <1.0 with signature change.

Usage examples: `ASTDiff().diff_files("a.py", "b.py")`

Known caveats or footguns: JS/TS parsers fall back to regex if tree-sitter is not installed. Rename detection only triggers when the same identifier exists in both files.
