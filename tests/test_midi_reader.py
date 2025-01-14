import pytest

from midi2cmd.midi_reader import CommandBindings, CommandKey


@pytest.fixture
def cmds():
    """Fixture to parse command keys from YAML."""
    channels = {
        "10": {
            "control": {
                "9": "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * " "512))",
                "18": "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h",
            },
            "pitch": "echo $MIDI_VALUE",
        }
    }
    c = CommandBindings()
    c.load(channels)
    return c


def test_yaml_reads_keys(cmds):
    assert CommandKey("10", "pitchwheel", None) in cmds
    assert CommandKey("10", "control_change", "9") in cmds
    assert CommandKey("10", "control_change", "18") in cmds


def test_yaml_no_extra_keys(cmds):
    assert len(cmds) == 3


def test_yaml_reads_commands(cmds):
    assert cmds[CommandKey("10", "pitchwheel", None)] == "echo $MIDI_VALUE"
    assert (
        cmds[CommandKey("10", "control_change", "9")]
        == "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))"
    )
    assert (
        cmds[CommandKey("10", "control_change", "18")]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )


def test_commands_from_iterable():
    c = CommandBindings()
    c[CommandKey(10, "control_change", 18)] = (
        "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )
    assert (
        c[CommandKey(10, "control_change", 18)]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )


def test_commands_init():
    c = CommandBindings([(CommandKey(10, "control_change", 18), "echo foo")])
    assert c[CommandKey(10, "control_change", 18)] == "echo foo"
