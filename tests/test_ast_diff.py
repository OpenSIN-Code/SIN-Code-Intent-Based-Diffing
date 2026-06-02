"""Tests for ASTDiff engine."""

import tempfile
from pathlib import Path

import pytest

from sin_code_ibd.ast_diff import ASTDiff
from sin_code_ibd.nodes import ChangeType


@pytest.fixture
def diff():
    return ASTDiff()


class TestDiffFiles:
    def test_identical_files(self, diff):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo(): pass\n")
            path = f.name
        try:
            changes = diff.diff_files(path, path)
            assert changes == []
        finally:
            Path(path).unlink()

    def test_simple_addition(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("def foo(): pass\n")
            b.write_text("def foo(): pass\ndef bar(): pass\n")
            changes = diff.diff_files(str(a), str(b))
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.ADDED
            assert changes[0].node.name == "bar"

    def test_simple_deletion(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("def foo(): pass\ndef bar(): pass\n")
            b.write_text("def foo(): pass\n")
            changes = diff.diff_files(str(a), str(b))
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.REMOVED
            assert changes[0].node.name == "bar"

    def test_signature_change(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("def foo(a): pass\n")
            b.write_text("def foo(a, b): pass\n")
            changes = diff.diff_files(str(a), str(b))
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.MODIFIED
            assert "foo" in changes[0].node.name

    def test_rename_detection(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("def foo(): pass\n")
            b.write_text("def bar(): pass\n")
            changes = diff.diff_files(str(a), str(b))
            # Since names differ, we detect as removed + added
            # But rename detection is based on same name moved — here names differ
            assert len(changes) == 2
            types = {c.change_type for c in changes}
            assert ChangeType.REMOVED in types
            assert ChangeType.ADDED in types

    def test_multiple_changes(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("def foo(): pass\nclass A: pass\n")
            b.write_text("def foo(): pass\nclass B: pass\n")
            changes = diff.diff_files(str(a), str(b))
            assert len(changes) == 2
            types = {c.change_type for c in changes}
            assert ChangeType.REMOVED in types
            assert ChangeType.ADDED in types


class TestDiffDirs:
    def test_multi_file_diff(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            dir_a = Path(tmp) / "a"
            dir_b = Path(tmp) / "b"
            dir_a.mkdir()
            dir_b.mkdir()
            (dir_a / "mod.py").write_text("def old(): pass\n")
            (dir_b / "mod.py").write_text("def new(): pass\n")
            changes = diff.diff_dirs(str(dir_a), str(dir_b))
            assert len(changes) == 2
            names = {c.node.name for c in changes}
            assert "old" in names
            assert "new" in names

    def test_file_added_in_dir(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            dir_a = Path(tmp) / "a"
            dir_b = Path(tmp) / "b"
            dir_a.mkdir()
            dir_b.mkdir()
            (dir_b / "new.py").write_text("def added(): pass\n")
            changes = diff.diff_dirs(str(dir_a), str(dir_b))
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.ADDED

    def test_file_removed_in_dir(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            dir_a = Path(tmp) / "a"
            dir_b = Path(tmp) / "b"
            dir_a.mkdir()
            dir_b.mkdir()
            (dir_a / "old.py").write_text("def removed(): pass\n")
            changes = diff.diff_dirs(str(dir_a), str(dir_b))
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.REMOVED

    def test_empty_dirs(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            dir_a = Path(tmp) / "a"
            dir_b = Path(tmp) / "b"
            dir_a.mkdir()
            dir_b.mkdir()
            changes = diff.diff_dirs(str(dir_a), str(dir_b))
            assert changes == []

    def test_nested_dirs(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            dir_a = Path(tmp) / "a"
            dir_b = Path(tmp) / "b"
            (dir_a / "sub").mkdir(parents=True)
            (dir_b / "sub").mkdir(parents=True)
            (dir_a / "sub" / "x.py").write_text("def f(): pass\n")
            (dir_b / "sub" / "x.py").write_text("def f(): pass\ndef g(): pass\n")
            changes = diff.diff_dirs(str(dir_a), str(dir_b))
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.ADDED


class TestEdgeCases:
    def test_empty_files(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("")
            b.write_text("")
            changes = diff.diff_files(str(a), str(b))
            assert changes == []

    def test_only_imports(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("import os\n")
            b.write_text("import os\nimport sys\n")
            changes = diff.diff_files(str(a), str(b))
            assert len(changes) == 1
            assert changes[0].change_type == ChangeType.ADDED

    def test_class_body_change(self, diff):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.py"
            b = Path(tmp) / "b.py"
            a.write_text("class A:\n    def m(self): pass\n")
            b.write_text("class A:\n    def m(self): return 1\n")
            changes = diff.diff_files(str(a), str(b))
            assert len(changes) >= 1
            assert any(c.change_type == ChangeType.MODIFIED for c in changes)
