import pytest

from compiler_admin.commands.time import time


@pytest.mark.parametrize("command", ["convert", "download"])
def test_time_commands(command):
    assert command in time.commands
