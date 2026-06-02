"""Tests for language parsers."""

import tempfile
from pathlib import Path

import pytest

from sin_code_ibd.parsers import get_parser, PythonParser, JSParser, TSParser


class TestAutoDetect:
    def test_python_extension(self):
        parser = get_parser("foo.py")
        assert isinstance(parser, PythonParser)

    def test_js_extension(self):
        parser = get_parser("foo.js")
        assert isinstance(parser, JSParser)

    def test_ts_extension(self):
        parser = get_parser("foo.ts")
        assert isinstance(parser, TSParser)


class TestPythonParser:
    def test_parse_function(self):
        parser = PythonParser()
        nodes = parser.parse_source("def foo(a, b): pass\n")
        assert len(nodes) == 1
        assert nodes[0]["name"] == "foo"
        assert nodes[0]["node_type"] == "FunctionDef"

    def test_parse_class(self):
        parser = PythonParser()
        nodes = parser.parse_source("class A:\n    def m(self): pass\n")
        names = {n["name"] for n in nodes}
        assert "A" in names
        assert "m" in names

    def test_parse_import(self):
        parser = PythonParser()
        nodes = parser.parse_source("import os\nfrom sys import path\n")
        assert len(nodes) == 2
        assert nodes[0]["node_type"] == "Import"
        assert nodes[1]["node_type"] == "ImportFrom"

    def test_parse_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def bar(): pass\n")
            path = f.name
        try:
            parser = PythonParser()
            nodes = parser.parse_file(path)
            assert len(nodes) == 1
            assert nodes[0]["name"] == "bar"
        finally:
            Path(path).unlink()

    def test_empty_source(self):
        parser = PythonParser()
        nodes = parser.parse_source("")
        assert nodes == []

    def test_async_function(self):
        parser = PythonParser()
        nodes = parser.parse_source("async def foo(): pass\n")
        assert nodes[0]["node_type"] == "AsyncFunctionDef"


class TestJSParser:
    def test_regex_parse(self):
        parser = JSParser()
        nodes = parser.parse_source("function foo() { return 1; }\n")
        assert len(nodes) == 1
        assert nodes[0]["name"] == "foo"

    def test_class_parse(self):
        parser = JSParser()
        nodes = parser.parse_source("class A {}\n")
        assert len(nodes) == 1
        assert nodes[0]["name"] == "A"


class TestTSParser:
    def test_regex_parse(self):
        parser = TSParser()
        nodes = parser.parse_source("function foo(): number { return 1; }\n")
        assert len(nodes) == 1
        assert nodes[0]["name"] == "foo"

    def test_interface_parse(self):
        parser = TSParser()
        nodes = parser.parse_source("interface Foo {}\n")
        assert len(nodes) == 1
        assert nodes[0]["name"] == "Foo"
