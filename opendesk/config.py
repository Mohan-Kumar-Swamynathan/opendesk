import os
import toml
from pathlib import Path
from typing import Optional


class Config:
    DEFAULT_CONFIG = {
        "permissions": {
            "allow_shell_commands": True,
            "allow_file_write": True,
            "allow_file_delete": False,
            "allow_input_control": True,
            "allow_process_kill": False,
        },
        "shell": {
            "denylist": [
                "rm -rf /",
                "format",
                "mkfs",
                "dd if=/dev/zero",
                "> /dev/sda",
            ]
        },
        "filesystem": {
            "allowed_write_paths": ["~/Desktop", "~/Documents", "~/Downloads"],
            "readonly_paths": ["~/.ssh", "~/.aws", "~/.config/opendesk"],
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.config/opendesk/config.toml")
        self.config = self._load_config()

    def _load_config(self) -> dict:
        path = Path(self.config_path)
        if path.exists():
            try:
                return toml.load(path)
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save(self):
        path = Path(self.config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        toml.dump(self.config, open(path, "w"))

    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value):
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def is_enabled(self, permission: str) -> bool:
        return self.get(f"permissions.{permission}", True)

    def get_denylist(self) -> list[str]:
        return self.get("shell.denylist", [])

    def is_path_allowed(self, path: str, write: bool = False) -> bool:
        path = os.path.expanduser(path)
        readonly = self.get("filesystem.readonly_paths", [])
        for ro_path in readonly:
            if path.startswith(os.path.expanduser(ro_path)):
                return False

        if write:
            allowed = self.get("filesystem.allowed_write_paths", [])
            if not allowed:
                return True
            for aw_path in allowed:
                if path.startswith(os.path.expanduser(aw_path)):
                    return True
            return False

        return True


config = Config()


def get_config() -> Config:
    return config