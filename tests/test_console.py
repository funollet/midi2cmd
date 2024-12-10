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
    assert "Usage:" in result.output
    assert "Print MIDI messages as they are received." in result.output
