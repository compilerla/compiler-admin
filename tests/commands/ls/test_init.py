import pytest

from compiler_admin.commands.ls import ls


@pytest.mark.parametrize(
    "command",
    ["groups", "orgs", "users"],
)
def test_user_commands(command):
    assert command in ls.commands
