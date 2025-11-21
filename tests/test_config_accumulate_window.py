"""Phase 1 tests for accumulate_window configuration parsing."""

import io

import pytest

from midi2cmd.midi_reader import ConfigTxt


def test_config_txt_default_accumulate_window():
    """Test that accumulate_window has a default value of 0.5 seconds."""
    config_txt = """
        port: Test Device
        control_change channel=10 control=9: echo foo
    """
    cfg = ConfigTxt.from_file(io.StringIO(config_txt))
    assert cfg.accumulate_window == 0.5


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1.5", 1.5),
        ("2", 2.0),
        ("0.1", 0.1),
        ("0.75", 0.75),
        ("    0.75", 0.75),
    ],
)
def test_config_txt_parse_accumulate_window_valid(value, expected):
    """Test parsing accumulate_window with various valid numeric values."""
    config_txt = f"""
        port: Test Device
        accumulate_window: {value}
        control_change channel=10 control=9: echo foo
    """
    cfg = ConfigTxt.from_file(io.StringIO(config_txt))
    assert cfg.accumulate_window == expected


@pytest.mark.parametrize(
    "value",
    [
        "-0.5",
        "0",
        "not_a_number",
        "0,1",
        "0.1 3",
    ],
)
def test_config_txt_accumulate_window_invalid(value):
    """Test that invalid accumulate_window values raise ValueError."""
    config_txt = f"""
        port: Test Device
        accumulate_window: {value}
        control_change channel=10 control=9: echo foo
    """
    with pytest.raises(ValueError):
        ConfigTxt.from_file(io.StringIO(config_txt))


def test_config_txt_accumulate_window_multiple_configs():
    """Test that accumulate_window is only parsed once (first occurrence wins)."""
    config_txt = """
        port: Test Device
        accumulate_window: 0.5
        control_change channel=10 control=9: echo foo
        accumulate_window: 2.0
        control_change channel=10 control=10: echo bar
    """
    cfg = ConfigTxt.from_file(io.StringIO(config_txt))
    # First occurrence should be kept
    assert cfg.accumulate_window == 0.5


def test_config_txt_accumulate_window_before_port():
    """Test that accumulate_window can be placed before port in config."""
    config_txt = """
        accumulate_window: 1.2
        port: Test Device
        control_change channel=10 control=9: echo foo
    """
    cfg = ConfigTxt.from_file(io.StringIO(config_txt))
    assert cfg.accumulate_window == 1.2
    assert cfg.port == "Test Device"


def test_config_txt_accumulate_window_preserved_with_other_settings():
    """Test that accumulate_window is preserved alongside other config."""
    config_txt = """
        port: My Device
        accumulate_window: 0.8
        control_change channel=10 control=9: pactl set-sink-volume @DEFAULT_SINK@ $MIDI_VALUE
        pitchwheel channel=10: xdotool key XF86AudioRaiseVolume
    """
    cfg = ConfigTxt.from_file(io.StringIO(config_txt))
    assert cfg.port == "My Device"
    assert cfg.accumulate_window == 0.8
    assert len(cfg.commands) == 2
