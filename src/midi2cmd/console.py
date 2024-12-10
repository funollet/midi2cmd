import click
from midi_reader import process_message, read_midi_messages
from mido import get_input_names


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option(
    "-p",
    "--port",
    "port_name",
    required=False,
    help="Name of the MIDI input port to use.",
)
@click.option(
    "-d",
    "--dump",
    is_flag=True,
    help="Print MIDI messages as they are received.",
)
def main(port_name, dump):
    """Read and print MIDI messages from the specified input port."""
    if not port_name:
        click.echo(main.get_help(click.Context(main)))
        click.Context(main).exit()
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
        process_message(message)


if __name__ == "__main__":
    main()
