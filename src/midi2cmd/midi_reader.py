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

    def for_message(self, msg):
        """Returns the command associated to a given message, or None"""
        key = CommandKey(msg.channel, msg.type, getattr(msg, "control", None))
        return self.get(key)


def process_message(message, cmd_mappings):
    cmd = cmd_mappings.for_message(message)
    if cmd:
        print(cmd)
