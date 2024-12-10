from collections import namedtuple

CommandKey = namedtuple("CommandKey", ["channel", "type", "control"])


def process_message(message, commands):

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
