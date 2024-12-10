from mido import open_input


def read_midi_messages(port_name):
    """Read and yield MIDI messages from the specified input port."""
    with open_input(port_name) as inport:
        for message in inport:
            yield message


def process_message(message):
    cmds = {
        (
            10,
            "control_change",
            9,
        ): "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))",
        (10, "control_change", 25): "xdotool key ctrl+shift+h",  # raise hand in Meet
        (10, "pitch"): "echo pitch changed",
    }
    cmd = cmds.get((message.type, message.control)) or cmds.get(
        (
            message.type,
            message.control,
            message.value,
        )
    )
    print(cmd)
