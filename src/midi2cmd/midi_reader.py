from dataclasses import InitVar, dataclass

from mido import Message


@dataclass(unsafe_hash=True)
class MessageKey:
    channel: int = 0
    type: str = ""
    control: int = 0
    # Init-only variable. Can receive a mido.Message to initialize the object.
    mido_message: InitVar[Message | None] = None

    def __post_init__(self, mido_message):
        if mido_message is not None:
            self.channel = mido_message.channel
            self.type = mido_message.type
            if hasattr(mido_message, "control"):
                self.control = mido_message.control

    def __setattr__(self, name: str, value) -> None:
        # Data validation: cast channel and control to integers.
        match name:
            case "channel":
                super().__setattr__(name, int(value))
            case "control":
                super().__setattr__(name, int(value))
            case _:
                super().__setattr__(name, value)


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
                key = MessageKey(channel, "pitchwheel")
                command = types["pitchwheel"]
                self[key] = command
            if "control_change" in types:
                for control, command in types["control_change"].items():
                    key = MessageKey(channel, "control_change", control)
                    self[key] = command

    def match(self, message: Message) -> str:
        """Return the command matching `message` or an empty string."""
        return self.get(MessageKey(mido_message=message), "")


def get_value(msg: Message) -> int:
    if hasattr(msg, "value"):
        return msg.value
    elif hasattr(msg, "pitch"):
        return msg.pitch
    else:
        return 0
