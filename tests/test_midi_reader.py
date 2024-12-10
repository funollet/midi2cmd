import pytest

from midi2cmd.midi_reader import CommandKey, Commands


@pytest.fixture
def cmds():
    """Fixture to parse command keys from YAML."""
    config_yaml = """
        channels:
          10:
            pitch: "echo $MIDI_VALUE"
            control:
              # control volume
              9: "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))"
              # raise hand in Meet
              18: "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    """
    c = Commands()
    c.from_yaml(config_yaml)
    return c


def test_yaml_reads_keys(cmds):
    assert CommandKey(10, "pitchwheel", None) in cmds
    assert CommandKey(10, "control_change", 9) in cmds
    assert CommandKey(10, "control_change", 18) in cmds


def test_yaml_no_extra_keys(cmds):
    assert len(cmds) == 3


def test_yaml_reads_commands(cmds):
    assert cmds[CommandKey(10, "pitchwheel", None)] == "echo $MIDI_VALUE"
    assert (
        cmds[CommandKey(10, "control_change", 9)]
        == "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))"
    )
    assert (
        cmds[CommandKey(10, "control_change", 18)]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )


def test_commands_from_iterable():
    c = Commands()
    c[CommandKey(10, "control_change", 18)] = (
        "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )
    assert (
        c[CommandKey(10, "control_change", 18)]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )


def test_commands_init():
    c = Commands([(CommandKey(10, "control_change", 18), "echo foo")])
    assert c[CommandKey(10, "control_change", 18)] == "echo foo"
