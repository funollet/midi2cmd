import os
import subprocess
from dataclasses import dataclass

from mido import Message


@dataclass(unsafe_hash=True)
class MessageKey:
    channel: int
    type: str
    control: int = 0

    @staticmethod
    def new(msg: Message):
        match msg.type:
            case "pitchwheel":
                return MessageKey(msg.channel, msg.type)
            case "control_change":
                return MessageKey(msg.channel, msg.type, msg.control)
            case _:
                raise Exception(f"message type {msg.type} not implemented")


class CommandBindings(dict):
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


def get_value(msg):
    match msg.type:
        case "pitchwheel":
            return msg.pitch
        case "control_change":
            return msg.value
        case _:
            raise Exception(f"message type {msg.type} not implemented")


def process_message(message: Message, cmd_mappings: CommandBindings):
    key = MessageKey.new(message)
    cmd = cmd_mappings.get(key, "")
    if cmd:
        env = os.environ.copy()
        env["MIDI_VALUE"] = str(get_value(message))
        subprocess.Popen(cmd, shell=True, env=env)
