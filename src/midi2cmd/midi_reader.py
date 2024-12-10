from collections import namedtuple

import yaml

CommandKey = namedtuple("CommandKey", ["channel", "type", "control"])


def load_commands_from_yaml(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)

    command_keys = {}
    for channel, types in config["channels"].items():
        if "pitch" in types:
            command = types["pitch"]
            command_keys[CommandKey(channel, "pitchwheel", None)] = command
        if "control" in types:
            for control, command in types["control"].items():
                command_keys[CommandKey(channel, "control_change", control)] = command

    return command_keys


def process_message(message):
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
