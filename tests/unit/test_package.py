"""Package tests."""
import subprocess
import sys

import pytest


def test_import_does_not_pollute_stdout(capsys):
    """Importing opendesk must not write to stdout."""
    result = subprocess.run(
        [sys.executable, "-c", "import opendesk"],
        capture_output=True,
        text=True,
    )
    assert result.stdout == "", f"opendesk import polluted stdout: {result.stdout!r}"


def test_version():
    from opendesk import __version__
    assert __version__ == "1.0.0"


def test_tool_decorator_marks_function():
    from opendesk import tool

    @tool
    def my_fn():
        pass

    assert my_fn._opendesk_tool is True
    assert my_fn._opendesk_tags == []


def test_tool_decorator_with_tags():
    from opendesk import tool

    @tool(tags=["read_only", "system"])
    def my_fn():
        pass

    assert my_fn._opendesk_tags == ["read_only", "system"]