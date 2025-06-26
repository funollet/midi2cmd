import os
import subprocess


def get_value(message):
    if message.type == "pitchwheel":
        return message.pitch
    if message.type == "control_change":
        return message.value


def process_message(message, cmd: str):
    value = get_value(message)
    env = os.environ.copy()
    env["MIDI_VALUE"] = str(value)
    if cmd:
        subprocess.Popen(cmd, shell=True, env=env)
