"""Diagnose opendesk setup."""
import json
import shutil
import subprocess
import sys
import time

from rich.console import Console

console = Console()


def run_doctor():
    console.print("[bold]Running diagnostics...[/bold]\n")

    results = []

    results.append(_check_opendesk_in_path())

    if sys.version_info >= (3, 10):
        results.append(("ok", "Python version OK"))
    else:
        results.append(("error", f"Python 3.10+ required, got {sys.version_info.major}.{sys.version_info.minor}"))

    results.append(_check_imports())
    results.append(_check_stdout_hygiene())
    results.append(_check_path_accessible())

    for status, msg in results:
        if status == "ok":
            console.print(f"[green]✓ {msg}[/green]")
        elif status == "warning":
            console.print(f"[yellow]⚠ {msg}[/yellow]")
        else:
            console.print(f"[red]✗ {msg}[/red]")


def _check_opendesk_in_path():
    path = shutil.which("opendesk")
    if not path:
        return ("error", "opendesk not in PATH")

    try:
        r = subprocess.run(
            [path, "--version"],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0:
            return ("ok", f"opendesk executable found: {path}")
        return ("error", f"Cannot execute: {r.stderr[:200]}")
    except Exception as e:
        return ("error", str(e))


def _check_imports():
    try:
        import opendesk
        from opendesk import tool
        from opendesk._stdio_hygiene import enforce_stdout_discipline
        return ("ok", "Core imports OK")
    except Exception as e:
        return ("error", f"Import failed: {e}")


def _check_stdout_hygiene():
    """Start server in subprocess, check stdout is pure JSON."""
    import select

    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "opendesk.cli", "--serve"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        ready, _, _ = select.select([proc.stdout], [], [], 2.0)

        if not ready:
            proc.terminate()
            return ("warning", "Server didn't respond — manual check needed")

        line = proc.stdout.readline()
        proc.terminate()

        if not line:
            return ("ok", "Server stdout clean")

        try:
            json.loads(line)
            return ("ok", "Server stdout is valid JSON")
        except json.JSONDecodeError:
            return ("error", f"Server stdout corrupted: {line[:100]!r}")
    except Exception as e:
        return ("warning", str(e))


def _check_path_accessible():
    """Check opendesk is reachable from a spawned subprocess."""
    path = shutil.which("opendesk")
    if not path:
        return ("error", "opendesk not in PATH — reinstall with: pip install opendesk")

    try:
        r = subprocess.run(
            [path, "--version"],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0:
            return ("ok", f"Executable at: {path}")
        return ("error", f"Cannot execute: {r.stderr[:200]}")
    except Exception as e:
        return ("error", str(e))