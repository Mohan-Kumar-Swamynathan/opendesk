"""Health check."""
from rich.console import Console
from rich.panel import Panel


def run_health():
    from opendesk.tools.system import get_system_info
    from opendesk import __version__
    from opendesk.platform_utils import get_os

    console = Console()
    info = get_system_info()
    title = f"System Health (opendesk {__version__} on {get_os()})"
    console.print(Panel(str(info), title=title)
)