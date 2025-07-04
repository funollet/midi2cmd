import mido
from mido import Message  # type: ignore[import-untyped]

from midi2cmd.midi_reader import ConfigTxt, MessageDict


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


# def test_messagedict_load():
#     channels = {
#         "10": {
#             "pitchwheel": "echo pitch",
#             "control_change": {"9": "echo control9", "18": "echo control18"},
#         },
#         "2": {"control_change": {"1": "echo c2-1"}},
#     }
#     mc = MessageDict()
#     mc.load(channels)
#     # Check pitchwheel
#     msg_pitch = mido.Message("pitchwheel", channel=10)
#     assert mc[msg_pitch] == "echo pitch"
#     # Check control_change 9
#     msg_c9 = mido.Message("control_change", channel=10, control=9)
#     assert mc[msg_c9] == "echo control9"
#     # Check control_change 18
#     msg_c18 = mido.Message("control_change", channel=10, control=18)
#     assert mc[msg_c18] == "echo control18"
#     # Check control_change 2-1
#     msg_c2_1 = mido.Message("control_change", channel=2, control=1)
#     assert mc[msg_c2_1] == "echo c2-1"
#     # Check missing
#     msg_missing = mido.Message("control_change", channel=3, control=1)
#     assert mc[msg_missing] == ""


def test_messagedict_unhandled_message_type():
    mc = MessageDict()
    # program_change is not handled by MessageDict logic
    msg = mido.Message("program_change", channel=10, program=10)
    # Should not raise, should return ""
    assert mc[msg] == ""


def test_parse_config_txt():
    import io

    config_txt = """
        port: X-TOUCH MINI MIDI 1
        #
        # Just show the pich change value.
        pitchwheel channel=10: echo $MIDI_VALUE
        # Control volume.
        control_change channel=10 control=9: pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))
        # Raise hand in Meet.
        control_change channel=10 control=18: [ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h
        control_change channel=6 control=9: echo foo
    """
    cfg = ConfigTxt.from_file(io.StringIO(config_txt))
    assert cfg.port == "X-TOUCH MINI MIDI 1"
    assert len(cfg.commands) == 4
    assert cfg.commands[Message("pitchwheel", channel=10)] == "echo $MIDI_VALUE"
    assert (
        cfg.commands[Message("control_change", channel=10, control=9)]
        == "pactl set-sink-volume @DEFAULT_SINK@ $((MIDI_VALUE * 512))"
    )
    assert (
        cfg.commands[Message("control_change", channel=10, control=18)]
        == "[ $MIDI_VALUE = 0 ] && xdotool key ctrl+shift+h"
    )
    assert cfg.commands[Message("control_change", channel=6, control=9)] == "echo foo"
