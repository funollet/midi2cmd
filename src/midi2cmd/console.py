import click
import mido
from midi_reader import read_midi_messages


@click.command()
@click.option('--port', 'port_name', required=True, help='Name of the MIDI input port to use.')
def main(port_name):
    """Read and print MIDI messages from the specified input port."""
    try:
        available_ports = mido.get_input_names()
        if port_name not in available_ports:
            raise click.BadParameter(f"Port '{port_name}' is not available. Available ports: {', '.join(available_ports)}")
    except Exception as e:
        raise click.ClickException(f"Error checking MIDI ports: {e}")

    for message in read_midi_messages(port_name):
        print(message)


if __name__ == "__main__":
    main()
