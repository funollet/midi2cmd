import os
import subprocess
from typing import Any

from mido import Message  # type: ignore[import-untyped]


def get_value(message: Message) -> int | None:
    if message.type == "pitchwheel":
        return message.pitch
    if message.type == "control_change":
        return message.value
    return None


def runcmd(cmd: str, **envvars: Any) -> None:
    """Runs cmd in a shell. Any key-value in envvars is added to the shell environment."""
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in envvars.items()})
    subprocess.run(cmd, shell=True, env=env)
