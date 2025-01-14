import os
import subprocess
from collections import namedtuple

CommandKey = namedtuple("CommandKey", ["channel", "type", "control"])


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
                key = CommandKey(channel, "pitchwheel", None)
                self.update({key: command})
            if "control" in types:
                for control, command in types["control"].items():
                    key = CommandKey(channel, "control_change", control)
                    self.update({key: command})

    def for_message(self, msg):
        """Returns the command associated to a given message, or None"""
        key = CommandKey(str(msg.channel), msg.type, getattr(msg, "control", None))
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
