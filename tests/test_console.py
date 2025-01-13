from unittest.mock import mock_open, patch

import typer
from pytest import raises
from typer.testing import CliRunner

from midi2cmd.console import app, load_config_toml, validate_midi_port


def test_load_config_toml_success():
    with patch("pathlib.Path.open", mock_open(read_data=b"")):
        result = load_config_toml("dummy_path")
        assert result == {}


def test_load_config_toml_file_not_found():
    with raises(typer.BadParameter, match="Can't read file non_existent_file."):
        load_config_toml("non_existent_file")


def test_validate_midi_port_valid():
    with patch("midi2cmd.console.open_input") as mock_open_input:
        mock_open_input.return_value.__enter__.return_value = None
        validate_midi_port("ValidPort")
        mock_open_input.assert_called_once_with("ValidPort")


def test_validate_midi_port_invalid():
    with raises(typer.BadParameter):
        with patch("midi2cmd.console.open_input", side_effect=OSError):
            validate_midi_port("InvalidPort")


def test_validate_midi_port_none():
    with raises(typer.BadParameter):
        validate_midi_port(None)


def test_cli_invalid_port():
    runner = CliRunner()
    with patch("midi2cmd.console.get_input_names", return_value=["ValidPort"]):
        result = runner.invoke(
            app,
            [
                "dump",
                "--port",
                "InvalidPort",
                "--config",
                "tests/fixtures/example.config.toml",
            ],
        )
        assert result.exit_code != 0
        assert "Invalid value: Port 'InvalidPort' is not available." in result.stdout


def test_cli_help_option():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_cli_list_ports():
    runner = CliRunner()
    with patch("midi2cmd.console.get_input_names", return_value=["Port1", "Port2"]):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Available MIDI input ports:" in result.output
        assert " Port1" in result.output
        assert " Port2" in result.output
