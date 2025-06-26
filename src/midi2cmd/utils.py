import os
import subprocess


def get_value(message):
    if message.type == "pitchwheel":
        return message.pitch
    if message.type == "control_change":
        return message.value


def runcmd(cmd, **envvars):
    """Runs cmd in a shell. Any key-value in envvars
    is added to the shell environment. Returns the command output."""
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in envvars.items()})
    result = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
    return result.stdout
