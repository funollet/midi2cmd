from pathlib import Path

import click
from mido import get_input_names, open_input

from midi2cmd.midi_reader import CommandBindings, process_message


@click.group()
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, readable=True),
    default=Path("~/.config/midi2cmd/config.yaml").expanduser(),
    help="Configuration file.",
)
@click.pass_context
def cli(ctx, config):
    """MIDI command line interface."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@cli.command()
@click.pass_context
def list(ctx):
    """List available MIDI input ports."""
    config = ctx.obj["config"]
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
    config = ctx.obj["config"]

    available_ports = get_input_names()
    if port_name not in available_ports:
        raise click.BadParameter(
            f"Port '{port_name}' is not available. Available ports: {', '.join(available_ports)}"
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

    available_ports = get_input_names()
    if port_name not in available_ports:
        raise click.BadParameter(
            f"Port '{port_name}' is not available. Available ports: {', '.join(available_ports)}"
        )

    cmd_bindings = CommandBindings()
    with config.open("r") as file:
        cmd_bindings.from_yaml(file)

    with open_input(port_name) as inport:
        for message in inport:
            process_message(message, cmd_bindings)


if __name__ == "__main__":
    cli()
