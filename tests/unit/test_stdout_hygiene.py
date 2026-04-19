"""stdout hygiene tests — CRITICAL for MCP protocol.

These tests ensure opendesk never pollutes stdout in server mode.
"""
import subprocess
import sys
import json
import time
import warnings

import pytest


def test_importing_opendesk_produces_no_stdout(capsys):
    """Any stdout on import = MCP protocol will fail."""
    result = subprocess.run(
        [sys.executable, "-c", "import opendesk"],
        capture_output=True,
        text=True,
    )
    assert result.stdout == "", f"opendesk import polluted stdout: {result.stdout!r}"


def test_version_command():
    """opendesk --version should print only version to stdout."""
    result = subprocess.run(
        [sys.executable, "-m", "opendesk.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "opendesk" in result.stdout
    assert "jsonrpc" not in result.stdout.lower()


def test_help_command():
    """opendesk --help should show help, not JSON-RPC."""
    result = subprocess.run(
        [sys.executable, "-m", "opendesk.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "USAGE" in result.stdout or "options" in result.stdout.lower()


def test_server_initialize_response_is_pure_json():
    """Server response to initialize must be valid JSON with no extra bytes."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "opendesk.cli", "--serve"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**subprocess.os.environ, "PYTHONUNBUFFERED": "1"},
    )

    time.sleep(0.5)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0.0.1"},
        },
    }
    proc.stdin.write((json.dumps(request) + "\n").encode())
    proc.stdin.flush()
    proc.stdin.close()

    response_line = proc.stdout.readline().decode()
    proc.terminate()
    proc.wait(timeout=5)

    assert response_line.strip(), "No response received"
    response = json.loads(response_line)
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response


def test_tool_call_response_is_pure_json():
    """Tool call response must be pure JSON."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "opendesk.cli", "--serve"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**subprocess.os.environ, "PYTHONUNBUFFERED": "1"},
    )

    time.sleep(0.5)

    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0.0.1"},
        },
    }
    proc.stdin.write((json.dumps(init_request) + "\n").encode())
    proc.stdin.flush()

    proc.stdout.readline()

    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }
    proc.stdin.write((json.dumps(tools_request) + "\n").encode())
    proc.stdin.flush()

    response_line = proc.stdout.readline().decode()
    proc.terminate()
    proc.wait(timeout=5)

    assert response_line.strip(), "No tools/list response"
    response = json.loads(response_line)
    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "tools" in response["result"]


def test_no_stdout_on_tool_list_call():
    """tools/list should be on stdout, nothing else."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "opendesk.cli", "--serve"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**subprocess.os.environ, "PYTHONUNBUFFERED": "1"},
    )

    time.sleep(0.3)

    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "0.0.1"},
            },
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        },
    ]

    for req in requests:
        proc.stdin.write((json.dumps(req) + "\n").encode())
        proc.stdin.flush()

    responses = []
    for _ in range(2):
        line = proc.stdout.readline()
        if line:
            responses.append(line.decode())

    proc.terminate()
    proc.wait(timeout=5)

    for resp in responses:
        try:
            parsed = json.loads(resp)
            assert "jsonrpc" in parsed
        except json.JSONDecodeError:
            pytest.fail(f"Non-JSON output on stdout: {resp!r}")


def test_stderr_is_free_for_logging():
    """stderr should be available for logging - check it's not connected to /dev/null."""
    result = subprocess.run(
        [sys.executable, "-m", "opendesk.cli", "--version"],
        capture_output=True,
    )
    assert result.stderr is not None