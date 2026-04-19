# opendesk Implementation Guide

## Architecture Overview

```
opendesk/
├── opendesk/
│   ├── __init__.py           # Version
│   ├── server.py           # MCP server
│   ├── cli.py            # CLI + Interactive mode
│   ├── config.py         # Security config
│   ├── platform_utils.py # OS detection
│   ├── ai_cli.py        # Keyword matching
│   └── llm/             # LLM backends (NEW)
│       ├── __init__.py
│       ├── base.py       # Abstract base class
│       ├── ollama.py    # Ollama backend
│       ├── claude_mcp.py # Claude MCP backend
│       ├── openai.py    # OpenAI/Anthropic
│       ├── custom.py    # Custom HTTP
│       └── direct.py    # Keyword matching
└── tools/               # 30+ tools
```

## LLM Backend System

### Interface

```python
from opendesk.llm.base import LLMBackend, LLMResponse

class LLMBackend(ABC):
    @property
    def name(self) -> str: pass
    
    @property
    def description(self) -> str: pass
    
    def is_available(self) -> bool: pass
    
    def chat(self, prompt: str, tools: list[dict], history: list[dict]) -> LLMResponse: pass

@dataclass
class LLMResponse:
    content: str
    tool_calls: list[dict]
```

### Available Backends

| Backend | Class | Requirements | Description |
|---------|-------|--------------|-------------|
| Ollama | `OllamaBackend` | Ollama running | Local, free |
| Claude MCP | `ClaudeMCPBackend` | MCP installed | Via MCP |
| OpenAI | `OpenAIBackend` | `OPENAI_API_KEY` | API |
| Anthropic | `AnthropicBackend` | `ANTHROPIC_API_KEY` | Claude API |
| Custom HTTP | `CustomHTTPBackend` | Configured URL | OpenAI-compatible |
| Direct | `DirectBackend` | Always | Keyword matching |

## Usage

### Quick Commands (No LLM)

```bash
opendesk -a battery      # Battery status
opendesk -a cpu         # CPU usage
opendesk -a memory      # RAM usage
opendesk -a screenshot  # Screenshot
```

### Direct Tool Call

```bash
opendesk get_system_info
opendesk list_processes limit=5
opendesk open_application app_name=Chrome
```

### Interactive Mode (with LLM)

```bash
opendesk --interactive
# Shows LLM selection menu
# User selects backend
# Natural language chat with tool execution
```

### MCP Server (for Claude Desktop)

```bash
opendesk --serve
# Connects to Claude Desktop via MCP
```

## Configuration

### Environment Variables

```bash
# Ollama
OLLAMA_MODEL=llama3.2

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229

# Custom LLM
CUSTOM_LLM_URL=http://localhost:8000/v1
CUSTOM_LLM_API_KEY=sk-...
CUSTOM_LLM_MODEL=gpt-3.5-turbo
```

### Config File

`~/.config/opendesk/config.toml`:

```toml
[llm]
default = "auto"

[llm.ollama]
model = "llama3.2"

[permissions]
allow_shell_commands = true
allow_file_write = true
allow_file_delete = false
```

## Adding New LLM Backend

Create a new file in `opendesk/llm/`:

```python
# opendesk/llm/my_backend.py
from opendesk.llm.base import LLMBackend, LLMResponse

class MyBackend(LLMBackend):
    def __init__(self, api_key: str = None):
        self._api_key = api_key
    
    @property
    def name(self) -> str:
        return "My LLM"
    
    @property
    def description(self) -> str:
        return "My custom LLM"
    
    def is_available(self) -> bool:
        return bool(self._api_key)
    
    def chat(self, prompt: str, tools: list[dict], history: list[dict] = None) -> LLMResponse:
        # Implement chat logic
        return LLMResponse(content="...", tool_calls=[])
```

Add to `__init__.py`:

```python
from opendesk.llm.my_backend import MyBackend

__all__ = [..., "MyBackend"]
```

## Tool Categories

| Category | Tools |
|----------|-------|
| Screen | take_screenshot, get_active_window, list_open_windows |
| Input | click, type_text, press_key, scroll, drag |
| File | read_file, write_file, list_directory, search_files |
| System | get_system_info, list_processes, kill_process |
| Apps | open_application, close_application, focus_application |
| Clipboard | get_clipboard, set_clipboard |
| Terminal | run_command |
| Notifications | send_notification |
| Audio | get_volume, set_volume, mute, unmute |
| Browser | get_open_tabs, open_url |

## Platform Support

| Feature | Mac | Windows | Linux |
|-------------|------|---------|
| All tools | ✅ | ✅ | ✅ |
| Ollama | ✅ | ✅ | ✅ |
| MCP | ✅ | ✅ | ✅ |
| Custom HTTP | ✅ | ✅ | ✅ |

## Examples

### With Ollama

```bash
# Start interactive
opendesk --interactive
# Select "1" for Ollama
# Type: "how many tabs in chrome?"
# LLM interprets and calls get_open_tabs
```

### MCP Integration

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "opendesk": {
      "command": "/path/to/opendesk/.venv/bin/opendesk",
      "args": ["--serve"]
    }
  }
}
```

### Custom LLM with LM Studio

```bash
export CUSTOM_LLM_URL=http://localhost:1234/v1
opendesk --interactive
# Select Custom
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama not found | Start Ollama: `ollama serve` |
| API key error | Set environment variable |
| Tools not working | Check MCP server running |
| Direct mode fallback | Select different LLM |

## License

MIT