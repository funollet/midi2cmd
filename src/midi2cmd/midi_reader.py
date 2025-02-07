from dataclasses import InitVar, dataclass

from mido import Message

from midi2cmd.utils import run


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
            match self.type:
                case "pitchwheel":
                    self.control = 0
                case "control_change":
                    self.control = mido_message.control
                case _:
                    raise Exception(f"message type {mido_message.type} not implemented")

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


def get_value(msg):
    match msg.type:
        case "pitchwheel":
            return msg.pitch
        case "control_change":
            return msg.value
        case _:
            raise Exception(f"message type {msg.type} not implemented")


def process_message(message: Message, cmd_mappings: CommandBindings):
    cmd = cmd_mappings.get(MessageKey(mido_message=message), "")
    env_vars = {"MIDI_VALUE": str(get_value(message))}
    run(cmd, env_vars)
