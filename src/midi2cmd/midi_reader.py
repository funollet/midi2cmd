import os
import subprocess
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class MessageKey:
    channel: int
    type: str
    control: int = 0


class CommandBindings(dict):
    # Usage:
    #
    # c = CommandBindings()
    # c[CommandKey(channel=10, type="control_change", control=18)] = "echo foo"

    def __init__(self, *args):
        super().__init__(*args)

    def load(self, channels):
        """Transforms a dict of channels to CommandBindings"""
        for channel, types in channels.items():
            if "pitch" in types:
                command = types["pitch"]
                key = MessageKey(int(channel), "pitchwheel")
                self.update({key: command})
            if "control" in types:
                for control, command in types["control"].items():
                    key = MessageKey(int(channel), "control_change", int(control))
                    self.update({key: command})

    def for_message(self, msg):
        """Returns the command associated to a given message, or ''"""
        key = MessageKey(str(msg.channel), msg.type, str(getattr(msg, "control", "")))
        return self.get(key)


def get_value(message):
    if message.type == "pitchwheel":
        return message.pitch
    if message.type == "control_change":
        return message.value


def process_message(message, cmd_mappings: CommandBindings):
    value = get_value(message)
    cmd = cmd_mappings.for_message(message)
    env = os.environ.copy()
    env["MIDI_VALUE"] = str(value)
    if cmd:
        subprocess.Popen(cmd, shell=True, env=env)
