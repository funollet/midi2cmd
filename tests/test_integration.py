"""Integration tests for midi2cmd using virtual MIDI device."""

import os
import signal
import subprocess
import time
from pathlib import Path

import pytest


@pytest.fixture
def config_path():
    """Return path to integration test config file."""
    return Path(__file__).parent / "fixtures" / "integration.config.txt"


@pytest.fixture
def virtual_device_script():
    """Return path to virtual MIDI device script."""
    return Path(__file__).parent.parent / "virtual_midi_device.py"


def test_midi2cmd_integration_with_virtual_device(config_path, virtual_device_script):
    """Test midi2cmd receives and processes messages from virtual MIDI device."""

    # Prepare environment
    env = os.environ.copy()
    env["WAIT_MODE"] = "signal"

    # Start virtual MIDI device in signal mode using uv run
    virtual_device = subprocess.Popen(
        ["uv", "run", "python3", str(virtual_device_script)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Give the virtual device time to create the MIDI port
    time.sleep(2.0)  # Increased wait time for port creation

    # Check if virtual device started successfully
    if virtual_device.poll() is not None:
        stdout, stderr = virtual_device.communicate()
        pytest.fail(
            f"Virtual device failed to start:\nstdout: {stdout}\nstderr: {stderr}"
        )

    # Start midi2cmd with the integration config using uv run
    midi2cmd = subprocess.Popen(
        [
            "uv",
            "run",
            "python3",
            "-m",
            "midi2cmd.console",
            "run",
            "--config",
            str(config_path),
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Give midi2cmd time to connect to the port
    time.sleep(0.5)

    try:
        # Send 5 messages by sending SIGUSR1 to virtual device
        expected_outputs = [
            "PITCHWHEEL:0",  # pitchwheel default pitch is 0
            "CC_CONTROL_9:64",  # control_change value=64
            "CC_CONTROL_18:0",  # control_change value=0
            "CC_CONTROL_26:127",  # control_change value=127
            "CC_CONTROL_1:1",  # control_change value=1
        ]

        for expected in expected_outputs:
            # Signal the virtual device to send next message
            virtual_device.send_signal(signal.SIGUSR1)
            time.sleep(0.2)  # Give time for message to be processed

        # Give a bit more time for final processing
        time.sleep(0.3)

        # Terminate midi2cmd gracefully
        midi2cmd.terminate()
        stdout, stderr = midi2cmd.communicate(timeout=2)

        # Verify outputs
        output_lines = stdout.strip().split("\n")

        # Check that we got all expected messages
        for expected in expected_outputs:
            assert (
                expected in output_lines
            ), f"Expected '{expected}' in output but got: {output_lines}"

        # Verify we got exactly 5 messages
        assert (
            len(output_lines) == 5
        ), f"Expected 5 output lines but got {len(output_lines)}: {output_lines}"

    finally:
        # Cleanup: terminate both processes
        if midi2cmd.poll() is None:
            midi2cmd.terminate()
            midi2cmd.wait(timeout=2)

        if virtual_device.poll() is None:
            virtual_device.terminate()
            virtual_device.wait(timeout=2)
