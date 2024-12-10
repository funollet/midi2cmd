import mido


def read_midi_messages(port_name):
    """Read and yield MIDI messages from the specified input port."""
    with mido.open_input(port_name) as inport:
        for message in inport:
            yield message


def main():
    # List available input ports
    print("Available MIDI input ports:")
    input_ports = mido.get_input_names()
    for port in input_ports:
        print(port)

    if not input_ports:
        print("No MIDI input ports available.")
    # Use the first available input port
    port_name = input_ports[0]
    for message in read_midi_messages(port_name):
        print(message)


if __name__ == "__main__":
    main()
