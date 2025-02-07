import os
import subprocess


def run(cmd: str, env_vars: dict[str, str]) -> None:
    """Run `cmd` in a shell. Adds every item in `env_vars` to the shell environment."""
    env = os.environ.copy()
    for k, v in env_vars.items():
        env[k] = v
    subprocess.Popen(cmd, shell=True, env=env)
