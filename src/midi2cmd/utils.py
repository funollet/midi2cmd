import os
import subprocess
from typing import Any


def run(cmd: str, env_vars: dict[str, str]) -> None:
    """Run `cmd` in a shell. Adds every item in `env_vars` to the shell environment."""
    env = os.environ.copy()
    for k, v in env_vars.items():
        env[k] = v
    subprocess.Popen(cmd, shell=True, env=env)


def dict_to_tuples(d: dict, parent_keys: tuple = ()) -> list[tuple[tuple, Any]]:
    """Flatten an structure of nested dicts into a list of tuples.

    Input example:

        { 1: {
            'dog': 'apple',
            'cat': {
                11: 'orange',
                12: 'banana',
                13: 'watermelon',
                }
            }
        }

    Output example:
        [
            ((1, 'dog'), 'apple')
            ((1, 'cat', 11), 'orange')
            ((1, 'cat', 12), 'banana')
            ((1, 'cat', 13), 'watermelon')
        ]
    """
    result = []
    for key, value in d.items():
        new_keys = parent_keys + (key,)
        if isinstance(value, dict):
            result.extend(dict_to_tuples(value, new_keys))
        else:
            result.append((new_keys, value))
    return result
