from collections import namedtuple

import yaml

CommandKey = namedtuple("CommandKey", ["channel", "type", "control"])


class CommandBindings(dict):
    # Usage:
    #
    # c = CommandBindings()
    # c[CommandKey(channel=10, type="control_change", control=18)] = "echo foo"

    def __init__(self, *args):
        super().__init__(*args)

    def from_yaml(self, source):
        """Gets a stream and parses yaml to CommandBindings"""
        config = yaml.safe_load(source)
        for channel, types in config["channels"].items():
            if "pitch" in types:
                command = types["pitch"]
                key = CommandKey(channel, "pitchwheel", None)
                self.update({key: command})
            if "control" in types:
                for control, command in types["control"].items():
                    key = CommandKey(channel, "control_change", control)
                    self.update({key: command})


def process_message(message):
    cmd_mappings = CommandBindings()
    with open("tests/fixtures/example.config.yaml", "r") as file:
        cmd_mappings.from_yaml(file)

    key = CommandKey(message.channel, message.type, getattr(message, "control", None))
    cmd = cmd_mappings.get(key)
    if cmd:
        print(cmd)
