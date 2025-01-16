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
        """Transforms a dict of channels to CommandBindings.

        Example of `channels`:

            { '10': {
                'pitchwheel': 'echo pitch [$MIDI_VALUE]',
                'control_change': {
                    '9': 'echo control 9 [$MIDI_VALUE]',
                    '18': 'echo control 18 [$MIDI_VALUE]',
                    '26': 'echo control 26 [$MIDI_VALUE]',
                    }
                }
            }
        """
        for channel, types in channels.items():
            if "pitchwheel" in types:
                key = MessageKey(channel=int(channel), type="pitchwheel")
                command = types["pitchwheel"]
                self[key] = command
            if "control_change" in types:
                for control, command in types["control_change"].items():
                    key = MessageKey(
                        channel=int(channel),
                        type="control_change",
                        control=int(control),
                    )
                    self[key] = command


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
