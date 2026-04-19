import builtins
import types

from opendesk.commands import ask, bridge


def test_run_ask_always_provides_tools(monkeypatch):
    captured = {}

    fake_ollama = types.SimpleNamespace()

    def fake_list():
        return {"models": [{"name": "llama3.2:latest"}]}

    def fake_chat(**kwargs):
        captured["kwargs"] = kwargs
        return {"message": {"content": "hello", "tool_calls": []}}

    fake_ollama.list = fake_list
    fake_ollama.chat = fake_chat

    monkeypatch.setattr(ask.shutil, "which", lambda _: "/usr/local/bin/ollama")
    monkeypatch.setattr(ask, "_build_registry", lambda: {"get_current_time": lambda: {}})
    monkeypatch.setattr(
        ask,
        "_build_tool_specs",
        lambda registry: [
            {
                "type": "function",
                "function": {"name": "get_current_time", "description": "Get time", "parameters": {"type": "object", "properties": {}, "required": []}},
            }
        ],
    )
    monkeypatch.setitem(__import__("sys").modules, "ollama", fake_ollama)

    ask.run_ask("hello there")

    assert "kwargs" in captured
    assert captured["kwargs"]["tools"] is not None
    assert len(captured["kwargs"]["tools"]) == 1


def test_run_bridge_always_provides_tools(monkeypatch):
    chat_calls = []

    fake_ollama = types.SimpleNamespace()

    def fake_list():
        return {"models": [{"name": "llama3.2:latest"}]}

    def fake_chat(**kwargs):
        chat_calls.append(kwargs)
        return {"message": {"content": "hi", "tool_calls": []}}

    fake_ollama.list = fake_list
    fake_ollama.chat = fake_chat

    monkeypatch.setattr(bridge.shutil, "which", lambda _: "/usr/local/bin/ollama")
    monkeypatch.setattr(bridge, "_check_internet", lambda: True)
    monkeypatch.setitem(__import__("sys").modules, "ollama", fake_ollama)

    monkeypatch.setattr(ask, "_build_registry", lambda: {"get_current_time": lambda: {}})
    monkeypatch.setattr(
        ask,
        "_build_tool_specs",
        lambda registry: [
            {
                "type": "function",
                "function": {"name": "get_current_time", "description": "Get time", "parameters": {"type": "object", "properties": {}, "required": []}},
            }
        ],
    )
    monkeypatch.setattr(ask, "_execute_tool", lambda name, args, registry: {})

    user_inputs = iter(["hello there", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(user_inputs))

    bridge.run_bridge()

    assert len(chat_calls) == 1
    assert chat_calls[0]["tools"] is not None
    assert len(chat_calls[0]["tools"]) == 1


def test_run_bridge_keeps_system_message_when_trimming(monkeypatch):
    first_roles = []

    fake_ollama = types.SimpleNamespace()

    def fake_list():
        return {"models": [{"name": "llama3.2:latest"}]}

    def fake_chat(**kwargs):
        first_roles.append(kwargs["messages"][0]["role"])
        return {"message": {"content": "ok", "tool_calls": []}}

    fake_ollama.list = fake_list
    fake_ollama.chat = fake_chat

    monkeypatch.setattr(bridge.shutil, "which", lambda _: "/usr/local/bin/ollama")
    monkeypatch.setattr(bridge, "_check_internet", lambda: True)
    monkeypatch.setitem(__import__("sys").modules, "ollama", fake_ollama)

    monkeypatch.setattr(ask, "_build_registry", lambda: {"get_current_time": lambda: {}})
    monkeypatch.setattr(
        ask,
        "_build_tool_specs",
        lambda registry: [
            {
                "type": "function",
                "function": {"name": "get_current_time", "description": "Get time", "parameters": {"type": "object", "properties": {}, "required": []}},
            }
        ],
    )
    monkeypatch.setattr(ask, "_execute_tool", lambda name, args, registry: {})

    user_inputs = iter([f"msg {i}" for i in range(45)] + ["quit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(user_inputs))

    bridge.run_bridge()

    assert len(first_roles) == 45
    assert all(role == "system" for role in first_roles)
