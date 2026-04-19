"""Plugin system with hot reload."""
import importlib.util
import logging
import shutil
import sys
import time
import traceback
from pathlib import Path
from threading import Thread
from typing import Optional

logger = logging.getLogger(__name__)

BUILTIN_TOOLS = frozenset([
    "take_screenshot", "get_active_window", "list_open_windows", "get_screen_text",
    "click", "type_text", "press_key", "scroll", "drag",
    "read_file", "write_file", "list_directory", "search_files", "get_recent_files",
    "move_file", "delete_file", "get_disk_usage",
    "list_processes", "kill_process", "get_system_info", "get_network_info",
    "open_application", "close_application", "focus_application", "list_installed_apps",
    "get_clipboard", "set_clipboard",
    "run_command", "get_command_history", "get_environment_variable",
    "send_notification",
    "get_volume", "set_volume", "mute", "unmute",
    "get_open_tabs", "open_url",
])

PLUGIN_TIMEOUT = 5.0

_plugin_modules = {}
_plugin_observer = None


def get_plugin_dir() -> Path:
    plugin_dir = Path.home() / ".config" / "opendesk" / "plugins"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    return plugin_dir


def setup_plugins(mcp) -> tuple[object, object]:
    """Set up plugin loading with hot reload."""
    global _plugin_observer

    _load_all_plugins(mcp)
    _plugin_observer = _PluginObserver(mcp)

    return (_plugin_modules, _plugin_observer)


def _load_all_plugins(mcp):
    """Load all plugins from plugin directory."""
    plugin_dir = get_plugin_dir()

    for plugin_file in plugin_dir.glob("*.py"):
        if plugin_file.name.startswith("_"):
            continue
        _load_plugin(mcp, plugin_file)


def _load_plugin(mcp, plugin_file: Path) -> bool:
    """Load a single plugin. Returns True on success."""
    plugin_name = plugin_file.stem

    if plugin_name in BUILTIN_TOOLS:
        logger.warning(f"Plugin {plugin_name} shadows built-in tool - rejected")
        return False

    spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
    if spec is None or spec.loader is None:
        return False

    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = module

        start = time.time()
        spec.loader.exec_module(module)
        elapsed = time.time() - start

        if elapsed > PLUGIN_TIMEOUT:
            logger.warning(f"Plugin {plugin_name} took {elapsed:.1f}s to load (slow)")

        for attr_name in dir(module):
            attr = getattr(module, attr_name, None)
            if callable(attr) and getattr(attr, "_opendesk_tool", False):
                tool_tags = getattr(attr, "_opendesk_tags", [])
                try:
                    mcp.tool(name=plugin_name, description=attr.__doc__ or "")(attr)
                    _plugin_modules[plugin_name] = module
                    logger.info(f"Loaded plugin: {plugin_name}")
                except Exception as e:
                    logger.error(f"Failed to register plugin {plugin_name}: {e}")

        return True

    except Exception as e:
        logger.error(f"Failed to load plugin {plugin_name}: {e}")
        traceback.print_exc()
        return False


def _unload_plugin(mcp, plugin_name: str):
    """Unload a plugin."""
    if plugin_name in _plugin_modules:
        del _plugin_modules[plugin_name]
    if plugin_name in sys.modules:
        del sys.modules[plugin_name]
    logger.info(f"Unloaded plugin: {plugin_name}"


class _PluginObserver:
    """File watcher for hot reload."""

    def __init__(self, mcp):
        self.mcp = mcp
        self._running = False
        self._thread: Optional[Thread] = None

    def start(self):
        """Start watching for file changes."""
        if self._running:
            return
        self._running = True
        self._thread = Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop watching."""
        self._running = False

    def _watch_loop(self):
        """Main watch loop."""
        import watchdog.observers
        import watchdog.events

        plugin_dir = get_plugin_dir()

        class _PluginHandler(watchdog.events.FileSystemEventHandler):
            def on_modified(self, event):
                if event.is_directory:
                    return
                if event.src_path.endswith(".py"):
                    plugin_name = Path(event.src_path).stem
                    _unload_plugin(self.mcp, plugin_name)
                    _load_plugin(self.mcp, Path(event.src_path))

        event_handler = _PluginHandler()
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, str(plugin_dir), recursive=False)
        observer.start()

        while self._running:
            time.sleep(1)

        observer.stop()
        observer.join()


def reload_plugin(mcp, plugin_name: str):
    """Manually reload a plugin."""
    plugin_dir = get_plugin_dir()
    plugin_file = plugin_dir / f"{plugin_name}.py"

    if not plugin_file.exists():
        logger.error(f"Plugin {plugin_name} not found")
        return False

    _unload_plugin(mcp, plugin_name)
    return _load_plugin(mcp, plugin_file)