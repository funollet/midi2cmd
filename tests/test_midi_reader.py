import tomllib

import pytest
from pytest import raises

from midi2cmd.midi_reader import CommandBindings, MessageKey


@pytest.fixture
def cmds():
    """Fixture to parse command keys from TOML."""
    txt = """
        [channels.10]
        pitch = "echo $MIDI_VALUE"
        control.9 = "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))"  # control volume
        control.18 = "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"            # raise hand in Meet
    """
    cfg = tomllib.loads(txt)
    c = CommandBindings()
    c.load(cfg["channels"])
    return c


def test_config_reads_keys(cmds):
    assert MessageKey(10, "pitchwheel") in cmds
    assert MessageKey(10, "control_change", 9) in cmds
    assert MessageKey(10, "control_change", 18) in cmds


def test_config_no_extra_keys(cmds):
    assert len(cmds) == 3


def test_config_reads_commands(cmds):
    assert cmds[MessageKey(10, "pitchwheel")] == "echo $MIDI_VALUE"
    assert (
        cmds[MessageKey(10, "control_change", 9)]
        == "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))"
    )
    assert (
        cmds[MessageKey(10, "control_change", 18)]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )


def test_commands_from_iterable():
    c = CommandBindings()
    c[MessageKey(10, "control_change", 18)] = (
        "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )
    assert (
        c[MessageKey(10, "control_change", 18)]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )


def test_commands_init():
    c = CommandBindings([(MessageKey(10, "control_change", 18), "echo foo")])
    assert c[MessageKey(10, "control_change", 18)] == "echo foo"


def test_dict_of_messagekey():
    d = {
        MessageKey(10, "control_change", 0): "a",
        MessageKey(10, "pitchwheel"): "b",
    }
    assert d[MessageKey(10, "control_change", 0)] == "a"
    assert d[MessageKey(10, "pitchwheel")] == "b"
    with raises(KeyError):
        d[MessageKey(99, "control_change", 0)]
