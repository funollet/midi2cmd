from pathlib import Path

import typer
import yaml
from mido import get_input_names, open_input

from midi2cmd.midi_reader import CommandBindings, process_message


def validate_midi_port(port):
    """Ensure a MIDI port can be opened."""
    if port is None:
        raise typer.BadParameter(
            f"Port '{port}' is not available. Hint: use `midi2cmd list`."
        )
    try:
        with open_input(port):
            pass
    except OSError:
        raise typer.BadParameter(
            f"Port '{port}' is not available. Hint: use `midi2cmd list`."
        )


def load_config_yaml(fname: str) -> str:
    """Return the contents of the config file."""
    cfg_yaml = ""
    try:
        with Path(fname).expanduser().open("r") as file:
            cfg_yaml = file.read()
    except FileNotFoundError:
        raise typer.BadParameter(f"Can't read file {fname}.")

    return yaml.safe_load(cfg_yaml)


app = typer.Typer()


@app.command("list")
def list_ports():
    """List available MIDI input ports."""
    available_ports = get_input_names()
    typer.echo("Available MIDI input ports:")
    for port in available_ports:
        typer.echo(f"    {port}")


@app.command()
def dump(
    config_path: str = typer.Option(
        "~/.config/midi2cmd/config.yaml", "--config", "-c", help="Configuration file."
    ),
    port: str = typer.Option(
        None, "--port", "-p", help="Name of the MIDI input port to use."
    ),
):
    """Print MIDI messages as they are received."""
    cfg = load_config_yaml(config_path)
    port = port or cfg.get("port")

    validate_midi_port(port)

    with open_input(port) as inport:
        for message in inport:
            typer.echo(f"{message}")


@app.command()
def run(
    config_path: str = typer.Option(
        "~/.config/midi2cmd/config.yaml", "--config", "-c", help="Configuration file."
    ),
    port: str = typer.Option(
        None, "--port", "-p", help="Name of the MIDI input port to use."
    ),
):
    """Run the MIDI command processor."""
    cfg = load_config_yaml(config_path)
    channels = cfg.get("channels")
    port = port or cfg.get("port")

    validate_midi_port(port)

    cmd_bindings = CommandBindings()
    cmd_bindings.load(channels)

    with open_input(port) as inport:
        for message in inport:
            process_message(message, cmd_bindings)


if __name__ == "__main__":
    app()
