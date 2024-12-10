import os

import pytest

from midi2cmd.midi_reader import CommandKey, load_commands_from_yaml


@pytest.fixture
def cmds():
    """Fixture to load command keys from a YAML configuration file."""
    yaml_file_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "example.config.yaml"
    )
    return load_commands_from_yaml(yaml_file_path)


def test_yaml_reads_keys(cmds):
    assert CommandKey(10, "pitchwheel", None) in cmds
    assert CommandKey(10, "control_change", 9) in cmds
    assert CommandKey(10, "control_change", 25) in cmds


def test_yaml_no_extra_keys(cmds):
    assert len(cmds) == 3


def test_yaml_reads_commands(cmds):
    assert cmds[CommandKey(10, "pitchwheel", None)] == "echo $MIDI_VALUE"
    assert (
        cmds[CommandKey(10, "control_change", 9)]
        == "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))"
    )
    assert (
        cmds[CommandKey(10, "control_change", 25)]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )
