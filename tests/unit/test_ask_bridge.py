"""Tests for opendesk ask and bridge commands.

Run:  pytest tests/test_ask_bridge.py -v
"""
import json
import inspect
import sys
from unittest.mock import patch, MagicMock
import pytest


# ──────────────────────────────────────────────────────────────
# ask.py unit tests
# ──────────────────────────────────────────────────────────────

class TestBuildRegistry:
    """Test the tool registry builder."""

    def test_registry_returns_dict(self):
        from opendesk.commands.ask import _build_registry
        reg = _build_registry()
        assert isinstance(reg, dict)

    def test_registry_has_tools(self):
        from opendesk.commands.ask import _build_registry
        reg = _build_registry()
        # Must have at least a few core tools
        assert len(reg) >= 5, f"Only {len(reg)} tools found"

    def test_registry_always_has_get_current_time(self):
        from opendesk.commands.ask import _build_registry
        reg = _build_registry()
        assert "get_current_time" in reg

    def test_get_current_time_works(self):
        from opendesk.commands.ask import _build_registry
        reg = _build_registry()
        result = reg["get_current_time"]()
        assert "time" in result
        assert "date" in result
        assert "weekday" in result

    def test_all_registry_values_are_callable(self):
        from opendesk.commands.ask import _build_registry
        reg = _build_registry()
        for name, func in reg.items():
            assert callable(func), f"{name} is not callable"

    def test_broken_import_doesnt_crash_registry(self):
        """A missing module should not prevent the registry from loading."""
        from opendesk.commands.ask import _build_registry
        # This should never raise, even if some tools fail to import
        reg = _build_registry()
        assert isinstance(reg, dict)


class TestBuildToolSpecs:
    """Test Ollama-compatible schema generation."""

    def test_specs_are_list(self):
        from opendesk.commands.ask import _build_registry, _build_tool_specs
        reg = _build_registry()
        specs = _build_tool_specs(reg)
        assert isinstance(specs, list)

    def test_each_spec_has_correct_structure(self):
        from opendesk.commands.ask import _build_registry, _build_tool_specs
        reg = _build_registry()
        specs = _build_tool_specs(reg)

        for spec in specs:
            assert spec["type"] == "function"
            fn = spec["function"]
            assert "name" in fn
            assert "description" in fn
            assert fn["description"], f"Empty description for {fn['name']}"
            assert "parameters" in fn
            assert fn["parameters"]["type"] == "object"
            assert "properties" in fn["parameters"]

    def test_specs_count_matches_registry(self):
        from opendesk.commands.ask import _build_registry, _build_tool_specs
        reg = _build_registry()
        specs = _build_tool_specs(reg)
        assert len(specs) == len(reg)

    def test_required_params_detected(self):
        """Functions with no-default params should list them as required."""
        from opendesk.commands.ask import _build_tool_specs

        def example_tool(path: str, limit: int = 10) -> dict:
            """Example tool."""
            return {}

        specs = _build_tool_specs({"example": example_tool})
        fn = specs[0]["function"]
        assert "path" in fn["parameters"]["required"]
        assert "limit" not in fn["parameters"]["required"]

    def test_type_mapping(self):
        """Python types should map to JSON schema types."""
        from opendesk.commands.ask import _build_tool_specs

        def typed_tool(a: str, b: int, c: float, d: bool) -> dict:
            """Typed."""
            return {}

        specs = _build_tool_specs({"typed": typed_tool})
        props = specs[0]["function"]["parameters"]["properties"]
        assert props["a"]["type"] == "string"
        assert props["b"]["type"] == "integer"
        assert props["c"]["type"] == "number"
        assert props["d"]["type"] == "boolean"


class TestPickModel:
    """Test model selection logic."""

    def test_picks_qwen_first(self):
        from opendesk.commands.ask import _pick_model
        models = ["llama3.2:latest", "qwen2.5:7b", "mistral:latest"]
        assert "qwen" in _pick_model(models)

    def test_falls_back_to_first_available(self):
        from opendesk.commands.ask import _pick_model
        models = ["some-random-model:latest"]
        assert _pick_model(models) == "some-random-model:latest"

    def test_returns_none_for_empty(self):
        from opendesk.commands.ask import _pick_model
        assert _pick_model([]) is None


class TestExecuteTool:
    """Test safe tool execution."""

    def test_executes_known_tool(self):
        from opendesk.commands.ask import _execute_tool

        def fake_tool(x: int = 5) -> dict:
            return {"result": x * 2}

        registry = {"fake_tool": fake_tool}
        result = _execute_tool("fake_tool", {"x": 3}, registry)
        assert result == {"result": 6}

    def test_returns_none_for_unknown_tool(self):
        from opendesk.commands.ask import _execute_tool
        result = _execute_tool("nonexistent", {}, {})
        assert result is None

    def test_handles_wrong_arguments(self):
        from opendesk.commands.ask import _execute_tool

        def strict_tool(required_arg: str) -> dict:
            return {"got": required_arg}

        registry = {"strict_tool": strict_tool}
        # Pass wrong kwargs — should not crash
        result = _execute_tool("strict_tool", {"wrong_key": "val"}, registry)
        assert result is not None
        assert "error" in result

    def test_handles_tool_exception(self):
        from opendesk.commands.ask import _execute_tool

        def crashing_tool() -> dict:
            raise RuntimeError("boom")

        registry = {"crasher": crashing_tool}
        result = _execute_tool("crasher", {}, registry)
        assert result is not None
        assert "error" in result
        assert "boom" in result["error"]


class TestRunAskPreflight:
    """Test run_ask pre-flight checks without actual Ollama."""

    @patch.dict(sys.modules, {"ollama": None})
    def test_missing_ollama_package_handled(self):
        """run_ask should not crash if ollama package is missing."""
        # Force ImportError
        from opendesk.commands import ask
        # Reload to pick up the patched import
        with patch("builtins.__import__", side_effect=ImportError("no module")):
            # Should print error, not raise
            try:
                ask.run_ask("test query")
            except SystemExit:
                pass  # acceptable
            except ImportError:
                pytest.fail("run_ask should handle ImportError gracefully")

    @patch("shutil.which", return_value=None)
    def test_missing_ollama_binary_handled(self, mock_which):
        """run_ask should tell user to install Ollama."""
        mock_ollama = MagicMock()
        with patch.dict(sys.modules, {"ollama": mock_ollama}):
            from opendesk.commands.ask import run_ask
            # Should return without crashing
            run_ask("test")


# ──────────────────────────────────────────────────────────────
# bridge.py unit tests
# ──────────────────────────────────────────────────────────────

class TestBridgeImport:
    """Bridge should import without side effects."""

    def test_import_no_stdout(self, capsys):
        import opendesk.commands.bridge  # noqa
        captured = capsys.readouterr()
        assert captured.out == "", f"bridge.py polluted stdout: {captured.out!r}"


class TestCheckInternet:
    """Test the connectivity checker."""

    def test_returns_bool(self):
        from opendesk.commands.bridge import _check_internet
        result = _check_internet()
        assert isinstance(result, bool)


# ──────────────────────────────────────────────────────────────
# Integration: console never writes to stdout
# ──────────────────────────────────────────────────────────────

class TestStdoutHygiene:
    """Neither module should write to stdout when imported."""

    def test_ask_import_clean(self, capsys):
        import opendesk.commands.ask  # noqa
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_bridge_import_clean(self, capsys):
        import opendesk.commands.bridge  # noqa
        captured = capsys.readouterr()
        assert captured.out == ""
