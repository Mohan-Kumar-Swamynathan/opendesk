# opendesk

**Open-source MCP server that gives AI full control of your desktop.**
Works on Mac, Windows, and Linux. Compatible with Claude, Cursor,
Ollama, and any MCP client.

[![PyPI version](https://img.shields.io/pypi/v/opendesk)](https://pypi.org/project/opendesk/)
[![Python](https://img.shields.io/pypi/pyversions/opendesk)](https://pypi.org/project/opendesk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-mac%20%7C%20windows%20%7C%20linux-blue)]()
[![MCP](https://img.shields.io/badge/MCP-compatible-green)]()

---

## What is opendesk?

opendesk is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server
that bridges AI assistants to your operating system.

Your AI can now:
- 📸 See your screen in real time
- 📁 Read and write your files
- ⚙️ Monitor CPU, RAM, and processes
- ⌨️ Control keyboard and mouse
- 🚀 Open and close applications
- 💻 Run terminal commands
- 🔔 Send desktop notifications
- 🔊 Control system audio

> **Privacy-first:** Everything runs locally. Zero telemetry. Zero cloud.

---

## Quick Start

```bash
pip install opendesk
```

Add to your AI client:

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "opendesk": {
      "command": "opendesk",
      "args": ["--serve"]
    }
  }
}
```

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "opendesk": {
      "command": "opendesk",
      "args": ["--serve"]
    }
  }
}
```

**Claude Code:**
```bash
claude mcp add opendesk -- opendesk --serve
```

**Local AI (Ollama — zero cloud):**
```bash
opendesk --serve --transport http --port 8765
python examples/ollama_bridge.py
```

---

## CLI Usage

```bash
opendesk --serve                          # Start MCP server (stdio)
opendesk --serve --transport http           # Start MCP server (HTTP)
opendesk --list-tools                   # List all available tools
opendesk --health                      # Run health check
opendesk --interactive                 # Interactive mode
opendesk --version                    # Show version
```

---

## Supported Clients

| Client | Status |
|--------|--------|
| Claude Desktop | ✅ Native |
| Cursor | ✅ Native |
| Claude Code | ✅ Native |
| Windsurf | ✅ Native |
| Zed | ✅ Native |
| Continue.dev | ✅ Native |
| Ollama (local) | ✅ Via bridge |
| LangChain | ✅ Via HTTP |

---

## Available Tools (30+)

### Screen & Vision
`take_screenshot` `get_active_window` `list_open_windows` `get_screen_text`

### Keyboard & Mouse
`click` `type_text` `press_key` `scroll` `drag`

### File System
`read_file` `write_file` `list_directory` `search_files`
`get_recent_files` `move_file` `delete_file` `get_disk_usage`

### System
`list_processes` `kill_process` `get_system_info` `get_network_info`

### Applications
`open_application` `close_application` `focus_application`

### Clipboard
`get_clipboard` `set_clipboard`

### Terminal
`run_command` `get_command_history` `get_environment_variable`

### Notifications & Audio
`send_notification` `get_volume` `set_volume` `mute` `unmute`

### Browser
`get_open_tabs` `open_url`

---

## Platform Support

| Feature | Mac | Windows | Linux |
|---------|-----|---------|-------|
| Screenshot | ✅ | ✅ | ✅ |
| File system | ✅ | ✅ | ✅ |
| Process control | ✅ | ✅ | ✅ |
| App control | ✅ | ✅ | ✅ |
| Input control | ✅ | ✅ | ✅ |
| Audio control | ✅ | ✅ | ✅ |
| Browser tabs | ✅ | ⚠️ | ⚠️ |

---

## Security

opendesk uses a **tiered permission model**:
- Destructive operations (`delete_file`, `kill_process`) are **off by default**
- Shell commands have a hardcoded denylist
- All file writes are bounded to allowed directories
- No data ever leaves your machine

Configuration file: `~/.config/opendesk/config.toml`

---

## License

MIT — free to use, modify, and distribute.

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).