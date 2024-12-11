from pathlib import Path

import click
from mido import get_input_names, open_input

from midi2cmd.midi_reader import CommandBindings, process_message


def validate_midi_port(port):
    """Ensure a MIDI port can be opened."""
    if port is None:
        raise click.BadParameter(
            f"Port '{port}' is not available. Hint: use `midi2cmd list`."
        )
    try:
        with open_input(port):
            pass
    except OSError:
        raise click.BadParameter(
            f"Port '{port}' is not available. Hint: use `midi2cmd list`."
        )


def load_config_yaml(fname: str) -> str:
    """Return the contents of the config file."""
    cfg_yaml = ""
    try:
        with Path(fname).expanduser().open("r") as file:
            cfg_yaml = file.read()
    except FileNotFoundError:
        raise click.BadParameter(f"Can't read file {fname}.")

    return cfg_yaml


@click.group()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(readable=True),
    default="~/.config/midi2cmd/config.yaml",
    help="Configuration file.",
)
@click.option(
    "-p",
    "--port",
    "port",
    help="Name of the MIDI input port to use.",
)
@click.pass_context
def cli(ctx, config_path, port):
    """MIDI command line interface."""

    # ctx.obj is used to store shared state or defaults between commands.
    ctx.ensure_object(dict)

    cfg_yaml = load_config_yaml(config_path)

    # Preserve parameters.
    ctx.obj["config"] = cfg_yaml
    ctx.obj["port"] = port


@cli.command()
def list():
    """List available MIDI input ports."""
    available_ports = get_input_names()
    click.echo("Available MIDI input ports:")
    for port in available_ports:
        click.echo(f"    {port}")


@cli.command()
@click.pass_context
def dump(ctx):
    """Print MIDI messages as they are received."""
    port = ctx.obj["port"]

    validate_midi_port(port)

    with open_input(port) as inport:
        for message in inport:
            click.echo(f"{message}")


@cli.command()
@click.pass_context
def run(ctx):
    """Run the MIDI command processor."""
    config, port = ctx.obj["config"], ctx.obj["port"]

    validate_midi_port(port)

    cmd_bindings = CommandBindings()
    cmd_bindings.from_yaml(config)

    with open_input(port) as inport:
        for message in inport:
            process_message(message, cmd_bindings)


if __name__ == "__main__":
    cli()
