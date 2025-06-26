from collections import namedtuple

from mido.frozen import freeze_message

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
                key = CommandKey(channel, "pitchwheel", "")
                self.update({key: command})
            if "control" in types:
                for control, command in types["control"].items():
                    key = CommandKey(channel, "control_change", control)
                    self.update({key: command})

    def for_message(self, msg):
        """Returns the command associated to a given message, or ''"""
        key = CommandKey(str(msg.channel), msg.type, str(getattr(msg, "control", "")))
        return self.get(key)


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
        message.time = 0
        if message.type == "pitchwheel":
            message.pitch = 0
        else:
            message.value = 0
        frozen_msg = freeze_message(message)
        return self.get(frozen_msg, "")
