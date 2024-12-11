from unittest.mock import mock_open, patch

import click
from click.testing import CliRunner
from pytest import raises

from midi2cmd.console import cli, load_config_yaml, validate_midi_port


def test_load_config_yaml_success():
    with patch("pathlib.Path.open", mock_open(read_data="is_yaml: true")):
        result = load_config_yaml("dummy_path")
        assert result == {"is_yaml": True}


def test_load_config_yaml_file_not_found():
    with raises(click.BadParameter, match="Can't read file non_existent_file."):
        load_config_yaml("non_existent_file")


def test_validate_midi_port_valid():
    with patch("midi2cmd.console.open_input") as mock_open_input:
        mock_open_input.return_value.__enter__.return_value = None
        validate_midi_port("ValidPort")
        mock_open_input.assert_called_once_with("ValidPort")


def test_validate_midi_port_invalid():
    with raises(click.BadParameter):
        with patch("midi2cmd.console.open_input", side_effect=OSError):
            validate_midi_port("InvalidPort")


def test_validate_midi_port_none():
    with raises(click.BadParameter):
        validate_midi_port(None)


def test_cli_invalid_port():
    runner = CliRunner()
    with patch("midi2cmd.console.get_input_names", return_value=["ValidPort"]):
        result = runner.invoke(cli, ["--port", "InvalidPort", "run"])
        assert result.exit_code != 0
        assert "Port 'InvalidPort' is not available." in result.output


def test_cli_help_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_cli_list_ports():
    runner = CliRunner()
    with patch("midi2cmd.console.get_input_names", return_value=["Port1", "Port2"]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Available MIDI input ports:" in result.output
        assert " Port1" in result.output
        assert " Port2" in result.output
