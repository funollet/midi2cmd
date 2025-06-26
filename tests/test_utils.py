from midi2cmd.utils import runcmd


def test_runcmd_echo_basic():
    output = runcmd("echo -n hello")
    assert output == "hello"


def test_runcmd_echo_with_envvar():
    output = runcmd("echo -n $FOO", FOO="bar")
    assert output == "bar"


def test_runcmd_echo_without_envvar():
    output = runcmd("echo -n $FOO")
    assert output == ""
