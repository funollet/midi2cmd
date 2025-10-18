#!/usr/bin/env python3
"""
Virtual MIDI device for testing midi2cmd.

This script creates a virtual MIDI port and sends MIDI messages
that can be read by midi2cmd for end-to-end testing.

Usage:
    # Signal mode (wait for SIGUSR1 to send each message):
    WAIT_MODE=signal python3 virtual_midi_device.py

    # Key mode (press Enter to send each message):
    WAIT_MODE=key python3 virtual_midi_device.py

    # Pause mode (automatically send messages every 1 second):
    WAIT_MODE=pause python3 virtual_midi_device.py

Default mode is 'key' if WAIT_MODE is not set.
"""

import os
import signal
import time
from dataclasses import dataclass

import mido

PORT_NAME = "miditest"

# Wait mode: 'signal', 'key', or 'pause'
# Can be overridden by WAIT_MODE environment variable
WAIT_MODE = os.environ.get("WAIT_MODE", "key")

# List of MIDI messages to send
MESSAGES = [
    mido.Message("pitchwheel", channel=10),
    mido.Message("control_change", channel=10, control=9, value=64),
    mido.Message("control_change", channel=10, control=18, value=0),
    mido.Message("control_change", channel=10, control=26, value=127),
    mido.Message("control_change", channel=10, control=1, value=1),
]


@dataclass
class VirtualMidiDevice:
    """Virtual MIDI device that sends messages on signal."""

    port_name: str

    def _wait_signal(self):
        """Wait for SIGUSR1 signal."""
        signal.signal(signal.SIGUSR1, lambda signum, frame: None)
        signal.pause()

    def _wait_key(self):
        """Wait for keypress."""
        input("Press Enter to send next message...")

    def _wait_pause(self):
        """Wait 1 second."""
        time.sleep(1)

    def run(self, messages: list, wait_mode: str = "signal"):
        """Create virtual MIDI port and send messages based on wait mode."""
        # Select wait function based on mode
        wait_funcs = {
            "signal": self._wait_signal,
            "key": self._wait_key,
            "pause": self._wait_pause,
        }
        wait_func = wait_funcs[wait_mode]

        # Create a virtual output port that midi2cmd can connect to
        with mido.open_output(self.port_name, virtual=True) as port:
            # Send each message after waiting
            for msg in messages:
                wait_func()
                port.send(msg)


def main():
    """Create a virtual MIDI port and send messages."""
    device = VirtualMidiDevice(port_name=PORT_NAME)
    device.run(messages=MESSAGES, wait_mode=WAIT_MODE)


if __name__ == "__main__":
    main()
