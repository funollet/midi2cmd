import mido
from mido.frozen import freeze_message  # type: ignore[import-untyped]


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

    def __setitem__(self, message, command):
        """Sets a message and its associated command."""
        # Default values for time, value, and pitch.
        message.time = 0
        if message.type == "pitchwheel":
            message.pitch = 0
        else:
            message.value = 0
        # Use freeze_message to ensure the message is hashable and can be used as a key.
        super().__setitem__(freeze_message(message), command)

    def __getitem__(self, message):
        """Returns the command associated to a given message, or ''."""
        # Normalize the message before comparing
        msg = message.copy()
        msg.time = 0
        if msg.type == "pitchwheel":
            msg.pitch = 0
        elif msg.type == "control_change":
            msg.value = 0
        # For unhandled types, just return ""
        else:
            return ""

        frozen_msg = freeze_message(msg)
        return self.get(frozen_msg, "")

    def load(self, channels):
        """Transforms a dict of channels to MessageDict."""
        for channel, types in channels.items():
            if "pitchwheel" in types:
                command = types["pitchwheel"]
                msg = mido.Message("pitchwheel", channel=int(channel))
                self[msg] = command
            if "control_change" in types:
                for control, command in types["control_change"].items():
                    msg = mido.Message(
                        "control_change", channel=int(channel), control=int(control)
                    )
                    self[msg] = command
