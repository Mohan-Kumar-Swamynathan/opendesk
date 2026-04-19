"""stdout hygiene — must be imported before anything else in server mode.

Prevents stdout corruption that breaks MCP protocol.
"""
import logging
import sys
import warnings


def enforce_stdout_discipline():
    """
    Redirect all logging, warnings, and print-like output to stderr.
    Call this FIRST in server mode — before any other imports.
    """
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
        force=True,
    )

    logging.captureWarnings(True)
    warnings.showwarning = _warning_to_stderr


def _warning_to_stderr(message, category, filename, lineno, file=None, line=None):
    """Send warnings to stderr, never stdout."""
    print(
        f"{filename}:{lineno}: {category.__name__}: {message}",
        file=sys.stderr
    )


class NoStdoutGuard:
    """Context manager that redirects any stdout writes to stderr + logs them."""

    def __init__(self, tool_name: str = "unknown"):
        self.tool_name = tool_name
        self.original_stdout = None

    def __enter__(self):
        self.original_stdout = sys.stdout
        sys.stdout = sys.stderr
        return self

    def __exit__(self, *args):
        sys.stdout = self.original_stdout