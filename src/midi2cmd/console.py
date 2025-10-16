from functools import partial
from pathlib import Path

import typer
from mido import get_input_names, open_input
from platformdirs import user_config_dir

from midi2cmd.midi_reader import ConfigTxt
from midi2cmd.utils import get_value, runcmd


def validate_midi_port(port: str | None):
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


def load_config_txt(fname: str) -> ConfigTxt:
    """Open a config file and arse its contents."""
    try:
        with Path(fname).open() as f:
            return ConfigTxt.from_file(f)
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
    return Path(user_config_dir("midi2cmd")) / "config.txt"


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
    cfg = load_config_txt(config_path)
    port = port or cfg.port

    validate_midi_port(port)
    process_messages(port, handlers=[echo_handler])


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
    cfg = load_config_txt(config_path)
    port = port or cfg.port
    validate_midi_port(port)

    cmd_handler = partial(msg_to_simple_cmd_mapper, cfg)
    process_messages(port, handlers=[cmd_handler])


def process_messages(port: str, handlers):
    with open_input(port) as inport:
        for message in inport:
            for handler in handlers:
                handler(message)


def echo_handler(message):
    typer.echo(f"{message}")


def msg_to_simple_cmd_mapper(cfg: ConfigTxt, message):
    cmd = cfg.commands[message]
    if cmd:
        runcmd(cmd, MIDI_VALUE=get_value(message))


if __name__ == "__main__":
    app()
