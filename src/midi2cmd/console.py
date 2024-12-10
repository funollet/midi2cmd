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
def main(port_name, dump):
    """Read and print MIDI messages from the specified input port."""

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
