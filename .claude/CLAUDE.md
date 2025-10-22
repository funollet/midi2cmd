# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is a CLI capable of reading events from a MIDI hardware device (knobs, sliders, buttons) and mapping them to system actions (shell commands, keyboard shortcuts, etc).

## Development Commands

All commands use `uv` and are scripted in the `justfile`:

- **Run all tests**: `just test` (runs unit tests, integration tests, and type checking)
- **Run unit tests only**: `just test-unit` or `uv run pytest tests/ --ignore=tests/test_integration.py`
- **Run integration tests only**: `just test-integration` or `uv run pytest tests/test_integration.py`
- **Type checking**: `just typecheck` or `uv run mypy src/ tests/`
- **Build package**: `just build` or `uv build`
- **Run the CLI**: `uv run midi2cmd` (with subcommands: `list`, `dump`, `run`)

## Architecture

### Core Components

- **`console.py`**: CLI entry point using Typer
  - `list` command: Lists available MIDI input ports
  - `dump` command: Prints raw MIDI messages (useful for debugging)
  - `run` command: Main command that processes MIDI messages and executes mapped commands
  - Loads config from `~/.config/midi2cmd/config.txt` by default

- **`midi_reader.py`**: Configuration parsing and message handling
  - `ConfigTxt`: Parses text-based config files mapping MIDI messages to shell commands
  - `MessageDict`: Custom dict that treats MIDI messages as keys, normalizing them by ignoring `time`, `value` (for control_change), and `pitch` (for pitchwheel) fields
  - Config format: `port: <midi_port_name>` followed by lines like `control_change channel=10 control=9: echo foo`

- **`utils.py`**: Helper functions
  - `get_value()`: Extracts value from MIDI messages (pitch for pitchwheel, value for control_change)
  - `runcmd()`: Executes shell commands with environment variables (e.g., `MIDI_VALUE`)

### Message Flow

1. User runs `midi2cmd run --config <config_file> --port <port_name>`
2. Config file is parsed into `ConfigTxt` with `MessageDict` for command lookup
3. MIDI port is opened via `mido.open_input()`
4. For each MIDI message received:
   - Message is normalized (time, value, pitch ignored)
   - Matched against config to find corresponding command
   - Command is executed via `runcmd()` with `MIDI_VALUE` env var

### Testing Infrastructure

- **Unit tests**: Test individual components (utils, midi_reader, console)
- **Integration tests**: Use `virtual_midi_device.py` to create a virtual MIDI port
  - Virtual device supports three wait modes: `signal` (SIGUSR1), `key` (Enter press), `pause` (auto 1s)
  - Integration tests use signal mode to control message timing
  - Tests verify end-to-end flow from MIDI input to command execution

## Python Tooling

- **Package manager**: uv (>=0.7.2 required)
- **Linting/formatting**: ruff (with import sorting enabled)
- **Type checking**: mypy (ignores missing type stubs for `mido`)
- **Testing**: pytest
- **Pre-commit hooks**: ruff (format and lint), security checks (no AWS creds, private keys, large files)
- **CI**: GitHub Actions runs type checking and unit tests on push/PR to master
- **Python version**: >=3.12

## Configuration File Format

The config file (`config.txt`) uses a simple line-based format:

```
port: <MIDI port name>
<midi_message_string>: <shell_command>
```

Example:

```
port: My MIDI Device
control_change channel=10 control=9: echo "Knob 9: $MIDI_VALUE"
pitchwheel channel=10: xdotool key XF86AudioRaiseVolume
```

MIDI messages are specified using mido's string format (see `mido.Message.from_str()`).

## Other Notes

- @~/.claude/shared-instructions.md
