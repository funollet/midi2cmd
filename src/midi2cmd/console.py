from pathlib import Path

import click
from mido import get_input_names, open_input

from midi2cmd.midi_reader import CommandBindings, process_message


@click.command()
@click.option(
    "-p",
    "--port",
    "port_name",
    help="Name of the MIDI input port to use.",
)
@click.option(
    "-d",
    "--dump",
    is_flag=True,
    required=False,
    help="Print MIDI messages as they are received.",
)
@click.option(
    "-l",
    "--list",
    "list_ports",
    is_flag=True,
    help="List available MIDI input ports.",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, readable=True),
    default=Path("~/.config/midi2cmd/config.yaml").expanduser(),
    help="Configuration file.",
)
def main(port_name, dump, list_ports, config):
    """Read and print MIDI messages from the specified input port or list available ports."""
    if list_ports:
        available_ports = get_input_names()
        click.echo("Available MIDI input ports:")
        for port in available_ports:
            click.echo(f"- {port}")
        return

    if port_name is None:
        click.echo("Error: Missing option '-p' / '--port'.")
        click.Context(main).exit(2)

    try:
        available_ports = get_input_names()
        if port_name not in available_ports:
            raise click.BadParameter(
                f"Port '{port_name}' is not available. Available ports: {', '.join(available_ports)}"
            )
    except Exception as e:
        raise click.ClickException(f"Error checking MIDI ports: {e}")

    cmd_bindings = CommandBindings()
    with config.open("r") as file:
        cmd_bindings.from_yaml(file)

    with open_input(port_name) as inport:
        for message in inport:
            if dump:
                click.echo(f"{message}")
            else:
                process_message(message, cmd_bindings)


if __name__ == "__main__":
    main()
