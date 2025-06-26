import os
import subprocess


def get_value(message):
    if message.type == "pitchwheel":
        return message.pitch
    if message.type == "control_change":
        return message.value


def runcmd(cmd, **envvars):
    """Runs cmd in a shell. Any key-value in envvars
    is added to the shell environment."""
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in envvars.items()})
    subprocess.Popen(cmd, shell=True, env=env)
