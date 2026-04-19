import subprocess
import os
from typing import Optional
from opendesk.platform_utils import OS, IS_MAC, IS_WINDOWS, IS_LINUX


def run_command(
    command: str,
    timeout: int = 30,
    working_directory: Optional[str] = None,
    shell: bool = True,
) -> dict:
    try:
        cwd = working_directory or os.path.expanduser("~")

        proc = subprocess.run(
            command if shell else command.split(),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            shell=shell,
        )

        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out", "exit_code": -1, "timed_out": True}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1, "timed_out": False}


def get_command_history(limit: int = 50) -> dict:
    history = []

    if IS_MAC:
        shell = os.environ.get("SHELL", "/bin/zsh")
        if "zsh" in shell:
            hist_file = os.path.expanduser("~/.zsh_history")
        else:
            hist_file = os.path.expanduser("~/.bash_history")
    elif IS_WINDOWS:
        return {"commands": [], "error": "Command history not available on Windows"}
    else:
        hist_file = os.path.expanduser("~/.bash_history")

    try:
        with open(hist_file, "r") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                line = line.strip()
                if line:
                    history.append(line)
    except FileNotFoundError:
        pass
    except Exception as e:
        return {"commands": [], "error": str(e)}

    return {"commands": history}


def get_environment_variable(key: str) -> dict:
    try:
        value = os.environ.get(key)
        return {"value": value, "exists": value is not None}
    except Exception as e:
        return {"value": None, "exists": False, "error": str(e)}