"""CLI entry point."""
import sys as _sys

if "--serve" in _sys.argv:
    from opendesk._stdio_hygiene import enforce_stdout_discipline
    enforce_stdout_discipline()

import argparse
from opendesk import __version__
from opendesk.platform_utils import OS


def _help_epilog():
    return """
EXAMPLES
  opendesk init                        Auto-configure AI clients
  opendesk doctor                      Diagnose setup
  opendesk -a cpu                      Quick CPU check
  opendesk ask "why is my Mac slow?"   Natural language (needs Ollama)
  opendesk audit                       See recent Claude actions
  opendesk --serve                     Start MCP server
  opendesk --serve --transport streamable-http  Start HTTP server

Documentation: https://github.com/Mohan-Kumar-Swamynathan/opendesk
"""


def main():
    parser = argparse.ArgumentParser(
        prog="opendesk",
        description="Open-source MCP server for AI desktop control.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_help_epilog(),
    )
    parser.add_argument("--version", action="version", version=f"opendesk {__version__}")
    parser.add_argument("--serve", action="store_true", help="Start MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    parser.add_argument("--port", type=int, default=8765, help="Port for HTTP transport")
    parser.add_argument("--list", action="store_true", help="List all tools")
    parser.add_argument("--health", action="store_true", help="Health check")
    parser.add_argument("-a", "--ask-check", help="Quick check: cpu, battery, memory, etc.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", help="Auto-configure MCP clients")
    sub.add_parser("doctor", help="Diagnose setup")
    sub.add_parser("uninstall", help="Remove opendesk from clients")
    sub.add_parser("tool", help="Call a tool directly: opendesk tool get_system_info")
    sub.add_parser("run", help="Alias for tool: opendesk run get_system_info")

    audit_p = sub.add_parser("audit", help="Show audit log")
    audit_p.add_argument("--limit", type=int, default=50)
    audit_p.add_argument("--today", action="store_true")
    audit_p.add_argument("--errors", action="store_true")
    audit_p.add_argument("--tool")
    audit_p.add_argument("--tail", action="store_true")

    ask_p = sub.add_parser("ask", help="Natural language query (needs Ollama)")
    ask_p.add_argument("query", nargs="+")
    ask_p.add_argument("--model")

    bridge_p = sub.add_parser("bridge", help="Interactive Ollama bridge")
    bridge_p.add_argument("--model", default="qwen2.5:7b")

    args, rest = parser.parse_known_args()

    try:
        _dispatch(args, rest)
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        _show_user_error(e)
        sys.exit(1)


def _dispatch(args, rest):
    if args.serve:
        from opendesk.commands.serve import run_serve
        run_serve(transport=args.transport, port=args.port)
    elif args.list:
        from opendesk.commands.list_tools import run_list
        run_list()
    elif args.health:
        from opendesk.commands.health import run_health
        run_health()
    elif args.ask_check:
        from opendesk.commands.check import run_check
        run_check(args.ask_check)
    elif args.command == "init":
        from opendesk.commands.init import run_init
        run_init()
    elif args.command == "doctor":
        from opendesk.commands.doctor import run_doctor
        run_doctor()
    elif args.command == "audit":
        from opendesk.commands.audit import run_audit
        run_audit(
            limit=args.limit, today_only=args.today,
            errors_only=args.errors, tool_filter=args.tool,
            tail=args.tail,
        )
    elif args.command == "ask":
        from opendesk.commands.ask import run_ask
        run_ask(" ".join(args.query), model=args.model)
    elif args.command == "bridge":
        from opendesk.commands.bridge import run_bridge
        run_bridge(model=args.model)
    elif args.command == "uninstall":
        from opendesk.commands.uninstall import run_uninstall
        run_uninstall()
    elif args.command in ("tool", "run"):
        from opendesk.commands.tool_call import run_tool
        run_tool(rest, dry_run=args.dry_run)
    elif rest:
        from opendesk.commands.tool_call import run_tool
        run_tool(rest, dry_run=args.dry_run)
    else:
        from opendesk.platform_utils import get_os
        from rich.console import Console
        from rich.markdown import Markdown

        console = Console()
        md = Markdown("""
# opendesk v{version}

**AI desktop control via MCP**

## GET STARTED
- `opendesk init` - Auto-configure AI clients
- `opendesk doctor` - Diagnose setup
- `opendesk --serve` - Start MCP server

## QUICK CHECKS
- `opendesk -a cpu` - CPU usage
- `opendesk -a battery` - Battery status
- `opendesk -a memory` - Memory usage

## SERVER
- `opendesk --serve` - Start stdio server
- `opendesk --serve --transport streamable-http` - Start HTTP server

Run `opendesk --help` for full options.
""".format(version=__version__))
        console.print(md)


def _show_user_error(e: Exception):
    from rich.console import Console

    console = Console(stderr=True)
    from opendesk.errors import OpendeskError

    if isinstance(e, OpendeskError):
        console.print(f"[red]❌ {e.message}[/red]")
        if e.suggestion:
            console.print(f"[yellow]💡 {e.suggestion}[/yellow]")
    else:
        console.print(f"[red]❌ Something went wrong: {e}[/red]")
        console.print("[dim]Run [cyan]opendesk doctor[/cyan] to diagnose.[/dim]")


if __name__ == "__main__":
    main()