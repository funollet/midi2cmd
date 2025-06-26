import tomllib
from pathlib import Path

import typer
from mido import get_input_names, open_input
from platformdirs import user_config_dir

from midi2cmd.midi_reader import CommandBindings
from midi2cmd.utils import get_value, runcmd


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


def load_config_toml(fname: str) -> dict[str, str]:
    """Return the contents of a toml config file."""
    try:
        with Path(fname).open("rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        raise typer.BadParameter(f"Can't read file {fname}.")


app = typer.Typer()


@app.command("list")
def list_ports():
    """List available MIDI input ports."""
    available_ports = get_input_names()
    typer.echo("Available MIDI input ports:")
    for port in available_ports:
        typer.echo(f"    {port}")


def default_config_path():
    return Path(user_config_dir("midi2cmd")) / "config.toml"


@app.command()
def dump(
    config_path: str = typer.Option(
        default_config_path(), "--config", "-c", help="Configuration file."
    ),
    port: str = typer.Option(
        None, "--port", "-p", help="Name of the MIDI input port to use."
    ),
):
    """Print MIDI messages as they are received."""
    cfg = load_config_toml(config_path)
    port = port or cfg.get("port", "")

    validate_midi_port(port)

    with open_input(port) as inport:
        for message in inport:
            typer.echo(f"{message}")


@app.command()
def run(
    config_path: str = typer.Option(
        default_config_path(), "--config", "-c", help="Configuration file."
    ),
    port: str = typer.Option(
        None, "--port", "-p", help="Name of the MIDI input port to use."
    ),
):
    """Run the MIDI command processor."""
    cfg = load_config_toml(config_path)
    channels = cfg.get("channels")
    port = port or cfg.get("port", "")

    validate_midi_port(port)

    cmd_bindings = CommandBindings()
    cmd_bindings.load(channels)

    with open_input(port) as inport:
        for message in inport:
            cmd = cmd_bindings.for_message(message)
            if cmd:
                runcmd(cmd, MIDI_VALUE=get_value(message))


if __name__ == "__main__":
    app()
