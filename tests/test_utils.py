import os
import tempfile

from midi2cmd.utils import runcmd


def test_runcmd_echo_basic():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.close()
        runcmd(f"echo -n hello > {tmp.name}")
        with open(tmp.name) as f:
            output = f.read()
        os.unlink(tmp.name)
    assert output == "hello"


def test_runcmd_echo_with_envvar():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.close()
        runcmd(f"echo -n $FOO > {tmp.name}", FOO="bar")
        with open(tmp.name) as f:
            output = f.read()
        os.unlink(tmp.name)
    assert output == "bar"


def test_runcmd_echo_without_envvar():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.close()
        runcmd(f"echo -n $FOO > {tmp.name}")
        with open(tmp.name) as f:
            output = f.read()
        os.unlink(tmp.name)
    assert output == ""
