import pytest

from compiler_admin.main import main


@pytest.mark.parametrize("command", ["info", "init", "time", "user"])
def test_main_commands(command):
    assert command in main.commands
