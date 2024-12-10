from unittest.mock import patch

from click.testing import CliRunner

from midi2cmd.console import main


def test_main_no_port():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "Error: Missing option '-p' / '--port'." in result.output


def test_main_invalid_port():
    runner = CliRunner()
    with patch("midi2cmd.console.get_input_names", return_value=["ValidPort"]):
        result = runner.invoke(main, ["--port", "InvalidPort"])
        assert result.exit_code != 0
        assert "Port 'InvalidPort' is not available." in result.output


def test_main_help_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0


def test_main_list_ports():
    runner = CliRunner()
    with patch("midi2cmd.console.get_input_names", return_value=["Port1", "Port2"]):
        result = runner.invoke(main, ["--list"])
        assert result.exit_code == 0
        assert "Available MIDI input ports:" in result.output
        assert "- Port1" in result.output
        assert "- Port2" in result.output
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Print MIDI messages as they are received." in result.output
