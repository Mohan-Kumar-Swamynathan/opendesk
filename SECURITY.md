# Security Policy

## Reporting Vulnerabilities

Please report security vulnerabilities to hello@opendesk.ai

## Security Model

opendesk uses a tiered permission system:

### Tier 1 — Always On (read-only)
- get_system_info, get_clipboard, get_active_window
- list_open_windows, get_volume, get_disk_usage
- list_directory (home only), get_network_info

### Tier 2 — Default On (common)
- take_screenshot, read_file, list_processes
- search_files, get_recent_files, send_notification
- open_url, get_open_tabs

### Tier 3 — Explicit Enable (powerful)
- run_command, write_file, delete_file
- kill_process, type_text, click

### Configuration

Create `~/.config/opendesk/config.toml`:

```toml
[permissions]
allow_shell_commands = true
allow_file_write = true
allow_file_delete = false
allow_input_control = true
allow_process_kill = false

[shell]
denylist = ["rm -rf /", "format", "mkfs"]

[filesystem]
allowed_write_paths = ["~/Desktop", "~/Documents"]
readonly_paths = ["~/.ssh", "~/.aws"]
```

## Rate Limiting

No rate limiting is currently implemented. Use with caution.

## Best Practices

1. Only enable Tier 3 permissions when needed
2. Review denylist regularly
3. Keep config in a secure location
4. Don't run in untrusted environments