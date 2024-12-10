import click
from mido import get_input_names

from midi2cmd.midi_reader import process_message, read_midi_messages


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
def main(port_name, dump, list_ports):
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

    for message in read_midi_messages(port_name):
        if dump:
            click.echo(f"Received message: {message}")
        else:
            process_message(message)


if __name__ == "__main__":
    main()
