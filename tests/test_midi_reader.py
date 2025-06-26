import tomllib

import mido
import pytest

from midi2cmd.midi_reader import CommandBindings, CommandKey, MessageDict


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


def test_config_reads_keys(cmds: CommandBindings):
    assert CommandKey("10", "pitchwheel", "") in cmds
    assert CommandKey("10", "control_change", "9") in cmds
    assert CommandKey("10", "control_change", "18") in cmds


def test_config_no_extra_keys(cmds: CommandBindings):
    assert len(cmds) == 3


def test_config_reads_commands(cmds: CommandBindings):
    assert cmds[CommandKey("10", "pitchwheel", "")] == "echo $MIDI_VALUE"
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


def test_messagedict_control_change_set_and_get():
    msg = mido.Message("control_change", channel=10, control=18, value=64)

    mc = MessageDict()
    mc[msg] = "echo foo"
    assert mc[msg] == "echo foo"


def test_messagedict_control_change_get_equivalent_items():
    msg1 = mido.Message("control_change", channel=10, control=18, value=64)
    msg2 = mido.Message("control_change", channel=10, control=18, value=33)

    mc = MessageDict()
    mc[msg1] = "echo foo"
    mc[msg2] = "echo bar"
    assert mc[msg1] == "echo bar"
    assert mc[msg2] == "echo bar"


def test_messagedict_control_change_time_ignored():
    msg1 = mido.Message("control_change", channel=10, control=18, value=64, time=100)
    msg2 = mido.Message("control_change", channel=10, control=18, value=64, time=200)

    mc = MessageDict()
    mc[msg1] = "echo foo"
    mc[msg2] = "echo bar"
    assert mc[msg1] == "echo bar"
    assert mc[msg2] == "echo bar"


def test_messagedict_pitchwheel_set_and_get():
    msg = mido.Message("pitchwheel", channel=10, pitch=200)

    mc = MessageDict()
    mc[msg] = "echo foo"
    assert mc[msg] == "echo foo"


def test_messagedict_pitchwheel_get_equivalent_items():
    msg1 = mido.Message("pitchwheel", channel=10, pitch=200)
    msg2 = mido.Message("pitchwheel", channel=10, pitch=1000)

    mc = MessageDict()
    mc[msg1] = "echo foo"
    mc[msg2] = "echo bar"
    assert mc[msg1] == "echo bar"
    assert mc[msg2] == "echo bar"


def test_messagedict_pitchwheel_time_ignored():
    msg1 = mido.Message("pitchwheel", channel=10, pitch=200, time=100)
    msg2 = mido.Message("pitchwheel", channel=10, pitch=200, time=200)

    mc = MessageDict()
    mc[msg1] = "echo foo"
    mc[msg2] = "echo bar"
    assert mc[msg1] == "echo bar"
    assert mc[msg2] == "echo bar"


def test_messagedict_no_command():
    mc = MessageDict()
    msg = mido.Message("control_change", channel=10, control=18, value=64)
    assert mc[msg] == ""


def test_messagedict_multiple_messages():
    mc = MessageDict()
    msg1 = mido.Message("control_change", channel=1, control=2, value=10)
    msg2 = mido.Message("pitchwheel", channel=1, pitch=200)
    mc[msg1] = "cmd1"
    mc[msg2] = "cmd2"
    assert mc[msg1] == "cmd1"
    assert mc[msg2] == "cmd2"
