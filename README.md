# opendesk

**AI-powered desktop control for Mac, Windows, and Linux.**

Give your AI assistant (Claude, Cursor, Ollama) full control of your desktop with 30+ tools.

![Demo](/docs/demo-hero.gif)

[![PyPI version](https://img.shields.io/pypi/v/opendesk)](https://pypi.org/project/opendesk/)
[![Python](https://img.shields.io/pypi/pyversions/opendesk)](https://pypi.org/project/opendesk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-mac%20%7C%20windows%20%7C%20linux-blue)]()

---

## Features

- 📸 **Screen Control** - Screenshot, window management, OCR
- ⌨️ **Input Automation** - Click, type, scroll, keyboard shortcuts
- 📁 **File Operations** - Read, write, search, move files
- ⚙️ **System Monitoring** - CPU, RAM, processes, network
- 🚀 **App Control** - Open, close, focus applications
- 📋 **Clipboard** - Read and write clipboard
- 🔔 **Notifications** - Send desktop notifications
- 🔊 **Audio** - Volume control, mute/unmute
- 🌐 **Browser** - Open URLs, list tabs

---

## Installation

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/opendesk
cd opendesk
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Or install from PyPI (when published)
pip install opendesk
```

---

## Quick Start

### Option 1: Quick CLI (No AI Needed)

```bash
# Just ask questions naturally
opendesk -a battery      # Battery status
opendesk -a cpu         # CPU usage
opendesk -a memory      # RAM usage
opendesk -a processes  # Top processes
opendesk -a files      # Recent files
opendesk -a disk      # Disk usage
opendesk -a clipboard # Clipboard content
```

### Option 2: Direct Tool Call

```bash
# Call any tool directly
opendesk get_system_info
opendesk list_processes limit=5
opendesk list_directory path=~ max_items=10
opendesk run_command command="ls -la"
opendesk get_volume
opendesk send_notification title="Hello" message="World"
```

### Option 3: Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "opendesk": {
      "command": "/path/to/opendesk/.venv/bin/opendesk",
      "args": ["--serve"]
    }
  }
}
```

Then restart Claude Desktop. You can say:
- "Take a screenshot"
- "Check my battery"
- "List running processes"
- "Open Terminal"
- "What's in my clipboard?"

### Option 4: Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "opendesk": {
      "command": "/path/to/opendesk/.venv/bin/opendesk",
      "args": ["--serve"]
    }
  }
}
```

![Demo](/docs/demo-cli.gif)

### Option 5: Local AI (Ollama)

> **Prerequisite:** Install [Ollama](https://ollama.com) first
> ```bash
> # Install Ollama, then pull a model:
> ollama pull llama3.2
> ```

Two ways to use with Ollama:

**Option A: One-off query**
```bash
opendesk ask "why is my Mac slow?"
opendesk ask "what is today's date?"
opendesk ask "open safari"
```

**Option B: Interactive bridge (loops until you quit)**
```bash
opendesk bridge
# Then type naturally:
# "hello"                 → Just chats
# "what time is it?"      → Returns current time
# "check my CPU"         → System info
# "open chrome"          → Opens app
# quit                  → Exit
```

![Demo](/docs/demo-local-ai.gif)

**Supported queries:**
- System: CPU, memory, battery, disk, processes, network
- Apps: open, close, focus applications
- Files: list directory, read/write files
- Clipboard: get/set
- Audio: volume, mute/unmute
- Time: date, time, weekday
- Screenshots, notifications

---

## Command Reference

### Quick Checks (`-a` flag)

| Ask | What It Does |
|-----|-------------|
| `opendesk -a battery` | Battery percentage and charging status |
| `opendesk -a cpu` | CPU usage percentage |
| `opendesk -a memory` | RAM usage |
| `opendesk -a disk` | Disk space |
| `opendesk -a processes` | Top 5 processes by memory |
| `opendesk -a files` | Files in home directory |
| `opendesk -a clipboard` | Current clipboard content |
| `opendesk -a network` | Network interfaces |
| `opendesk -a screenshot` | Take a screenshot |
| `opendesk -a volume` | Audio volume level |

### Direct Tool Calls

#### Screen & Vision

| Command | Example |
|---------|--------|
| `take_screenshot` | `opendesk take_screenshot` |
| `get_active_window` | `opendesk get_active_window` |
| `list_open_windows` | `opendesk list_open_windows` |
| `get_screen_text` | `opendesk get_screen_text` (OCR) |

What to ask AI: *"Take a screenshot"*, *"What window is active?"*, *"List all open windows"*, *"Read the text on screen"*

#### Input Automation

| Command | Example |
|---------|--------|
| `click` | `opendesk click x=100 y=200` |
| `type_text` | `opendesk type_text text="Hello"` |
| `press_key` | `opendesk press_key key="cmd+c"` |
| `scroll` | `opendesk scroll direction=up amount=3` |
| `drag` | `opendesk drag from_x=100 from_y=200 to_x=300 to_y=400` |

What to ask AI: *"Click at 100, 200"*, *"Type hello world"*, *"Press cmd+c"*, *"Scroll down"*, *"Drag from here to there"*

#### File System

| Command | Example |
|---------|--------|
| `read_file` | `opendesk read_file path=~/notes.txt` |
| `write_file` | `opendesk write_file path=~/test.txt content="Hello"` |
| `list_directory` | `opendesk list_directory path=. max_items=10` |
| `search_files` | `opendesk search_files query="*.py"` |
| `get_recent_files` | `opendesk get_recent_files days=7` |
| `move_file` | `opendesk move_file source=~/a.txt destination=~/b.txt` |
| `delete_file` | `opendesk delete_file path=~/temp.txt` |
| `get_disk_usage` | `opendesk get_disk_usage` |

What to ask AI: *"Read my notes.txt"*, *"Write this to a file"*, *"List files in Documents"*, *"Find all Python files"*, *"What did I recently download?"*, *"Move this file to Desktop"*, *"Delete temp.txt"*, *"How much disk space?"*

#### System

| Command | Example |
|---------|--------|
| `list_processes` | `opendesk list_processes limit=10` |
| `kill_process` | `opendesk kill_process identifier="Safari"` |
| `get_system_info` | `opendesk get_system_info` |
| `get_network_info` | `opendesk get_network_info` |

What to ask AI: *"What processes are running?"*, *"Kill Safari"*, *"System info"*, *"Network status"*

#### Applications

| Command | Example |
|---------|--------|
| `open_application` | `opendesk open_application app_name="Safari"` |
| `close_application` | `opendesk close_application app_name="Safari"` |
| `focus_application` | `opendesk focus_application app_name="Terminal"` |
| `list_installed_apps` | `opendesk list_installed_apps` |

What to ask AI: *"Open Safari"*, *"Close Chrome"*, *"Switch to Terminal"*, *"What apps are installed?"*

#### Clipboard

| Command | Example |
|---------|--------|
| `get_clipboard` | `opendesk get_clipboard` |
| `set_clipboard` | `opendesk set_clipboard content="Hello"` |

What to ask AI: *"What's in my clipboard?"*, *"Copy this text"*

#### Terminal

| Command | Example |
|---------|--------|
| `run_command` | `opendesk run_command command="ls -la"` |
| `get_command_history` | `opendesk get_command_history limit=10` |
| `get_environment_variable` | `opendesk get_environment_variable key="PATH"` |

What to ask AI: *"Run ls -la"*, *"Show my command history"*, *"What's my PATH?"*

#### Notifications

| Command | Example |
|---------|--------|
| `send_notification` | `opendesk send_notification title="Hey" message="Done!"` |

What to ask AI: *"Notify me when done"*, *"Send a notification"*

#### Audio

| Command | Example |
|---------|--------|
| `get_volume` | `opendesk get_volume` |
| `set_volume` | `opendesk set_volume level=50` |
| `mute` | `opendesk mute` |
| `unmute` | `opendesk unmute` |

What to ask AI: *"Volume?"*, *"Set volume to 50"*, *"Mute"*, *"Unmute"*

#### Browser

| Command | Example |
|---------|--------|
| `get_open_tabs` | `opendesk get_open_tabs` |
| `open_url` | `opendesk open_url url="https://example.com"` |

What to ask AI: *"What tabs do I have open?"*, *"Open example.com"*

---

## Claude Desktop Examples

Here are exact prompts you can use with Claude Desktop when opendesk is connected:

### Screen & Vision
```
"Take a screenshot and save it to Desktop"
"What is my current active window?"
"List all my open windows"
"Read the text on my screen"
```

### File Operations
![Demo](/docs/demo-files.gif)
```
"Read the contents of ~/Documents/notes.txt"
"Create a new file called todo.txt with this list"
"List all files in my Downloads folder"
"Find all Python files in my project"
"What did I download recently?"
"Move screenshot.png to Pictures folder"
"Delete the temporary file"
"How much free disk space do I have?"
```

### System Monitoring
```
"What is my CPU usage right now?"
"How much memory am I using?"
"List my top 5 processes by memory"
"Kill the process named Slack"
"Show me system information"
"Is my wifi connected?"
```

### Application Control
```
"Open Safari browser"
"Close Chrome"
"Switch to Terminal"
"What applications are installed?"
```

### Clipboard
```
"What's in my clipboard?"
"Copy this text to clipboard"
```

### Notifications
```
"Send me a notification when the download finishes"
```

### Audio
```
"What is the current volume?"
"Set volume to 75%"
"Mute the audio"
```

---

## MCP Server Mode

For developers who want to integrate with custom clients:

```bash
# Start MCP server (stdio - for Claude Desktop, Cursor)
opendesk --serve

# Start MCP server (HTTP - for web apps)
opendesk --serve --transport http --port 8765

# List all available tools
opendesk --list

# Health check
opendesk --health
```

---

## Security

opendesk runs locally - no data leaves your machine.

- Destructive commands (delete, kill) are off by default
- Config file: `~/.config/opendesk/config.toml`
- See [SECURITY.md](SECURITY.md) for details

---

## Platform Support

| Feature | Mac | Windows | Linux |
|---------|-----|---------|-------|
| Screenshot | ✅ | ✅ | ✅ |
| File system | ✅ | ✅ | ✅ |
| Process control | ✅ | ✅ | ✅ |
| App control | ✅ | ✅ | ✅ |
| Input control | ✅ | ✅ | ✅ |
| Audio | ✅ | ✅ | ✅ |
| Browser tabs | ✅ | ⚠️ | ⚠️ |

---

## License

MIT — free to use, modify, and distribute.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

Questions? Open an issue!