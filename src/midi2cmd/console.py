from pathlib import Path

import click
from mido import get_input_names, open_input

from midi2cmd.midi_reader import CommandBindings, process_message


@click.group()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(readable=True),
    default="~/.config/midi2cmd/config.yaml",
    help="Configuration file.",
)
@click.pass_context
def cli(ctx, config_path):
    """MIDI command line interface."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path

    # Load config file.
    cfg_yaml = ""
    try:
        with Path(config_path).expanduser().open("r") as file:
            cfg_yaml = file.read()
    except FileNotFoundError:
        raise click.BadParameter(f"Can't read file {config_path}.")
    # Pass contents of config file as 'config'.
    ctx.obj["config"] = cfg_yaml


@cli.command()
@click.pass_context
def list(ctx):
    """List available MIDI input ports."""
    available_ports = get_input_names()
    click.echo("Available MIDI input ports:")
    for port in available_ports:
        click.echo(f"- {port}")


@cli.command()
@click.option(
    "-p",
    "--port",
    "port_name",
    help="Name of the MIDI input port to use.",
    required=True,
)
@click.pass_context
def dump(ctx, port_name):
    """Print MIDI messages as they are received."""
    # config = ctx.obj["config"]

    try:
        with open_input(port_name) as inport:
            pass
    except OSError:
        raise click.BadParameter(
            f"Port '{port_name}' is not available. Hint: use `midi2cmd list`."
        )

    with open_input(port_name) as inport:
        for message in inport:
            click.echo(f"{message}")


@cli.command()
@click.option(
    "-p",
    "--port",
    "port_name",
    help="Name of the MIDI input port to use.",
    required=True,
)
@click.pass_context
def run(ctx, port_name):
    """Run the MIDI command processor."""
    config = ctx.obj["config"]

    try:
        with open_input(port_name) as inport:
            pass
    except OSError:
        raise click.BadParameter(
            f"Port '{port_name}' is not available. Hint: use `midi2cmd list`."
        )

    cmd_bindings = CommandBindings()
    cmd_bindings.from_yaml(config)

    with open_input(port_name) as inport:
        for message in inport:
            process_message(message, cmd_bindings)


if __name__ == "__main__":
    cli()
