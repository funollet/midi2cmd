from typing import IO, Any

import mido
from mido.frozen import (  # type: ignore[import-untyped]
    Message,
    freeze_message,
)


class MessageDict(dict):
    """
    A dict with mido.Message's as keys.
    Two messages are considered equal ignoring fields 'time', 'value' (for control_change events),
    and 'pitch' (for pitchwheel events).

    Usage:

        msg1 = mido.Message("control_change", channel=1, control=2)
        msg2 = mido.Message("control_change", channel=1, control=2, value=10)

        mc = MessageDict()
        mc[msg1] = "echo foo"
        mc[msg2]                   # returns "echo foo"
    """

    def __init__(self, *args):
        super().__init__(*args)

    @staticmethod
    def _normalize(message: Message) -> Any:
        """Normalize a message by setting time, value, and pitch to default values."""
        msg = message.copy()
        # Default values for time, value, and pitch.
        msg.time = 0
        if msg.type == "pitchwheel":
            msg.pitch = 0
        elif msg.type == "control_change":
            msg.value = 0
        # Use freeze_message to ensure the message is hashable and can be used as a key.
        return freeze_message(msg)

    def __setitem__(self, message: Message, command: str) -> None:
        """Sets a message and its associated command."""
        super().__setitem__(self._normalize(message), command)

    def __getitem__(self, message: Message) -> str:
        """Returns the command associated to a given message, or ''."""
        # For unhandled types, just return ""
        if message.type not in ["pitchwheel", "control_change"]:
            return ""

        return self.get(self._normalize(message), "")


def parse_config_txt(txt: IO[str]) -> dict[str, Any]:
    """Parse a config txt file object in the plain text format (see example.config.txt).
    Returns a tuple with the port and a MessageDict of commands.
    """
    port = ""
    commands = MessageDict()

    for line in txt:  # Iterate directly over the file object
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("port:"):
            port = line.split(":", 1)[1].strip()
        else:
            message, cmd = line.split(":", 1)
            commands[mido.Message.from_str(message)] = cmd.strip()

    return {"port": port, "channels": commands}
