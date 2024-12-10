import click
from midi_reader import read_midi_messages


@click.command()
@click.option('--port', 'port_name', required=True, help='Name of the MIDI input port to use.')
def main(port_name):
    """Read and print MIDI messages from the specified input port."""
    for message in read_midi_messages(port_name):
        print(message)


if __name__ == "__main__":
    main()
