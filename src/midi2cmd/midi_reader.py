from collections import namedtuple

from mido import open_input


def read_midi_messages(port_name):
    """Read and yield MIDI messages from the specified input port."""
    with open_input(port_name) as inport:
        for message in inport:
            yield message


def process_message(message):
    CommandKey = namedtuple("CommandKey", ["channel", "type", "control"])

    cmds = {
        CommandKey(
            10, "control_change", 9
        ): "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))",
        CommandKey(
            10, "control_change", 18
        ): "xdotool key ctrl+shift+h",  # raise hand in Meet
        CommandKey(10, "pitchwheel", None): "echo pitch changed",
    }

    key = CommandKey(message.channel, message.type, getattr(message, "control", None))
    cmd = cmds.get(key)
    if cmd:
        print(cmd)
