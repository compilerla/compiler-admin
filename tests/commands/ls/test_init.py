import pytest

from compiler_admin.commands.ls import ls


@pytest.mark.parametrize(
    "command",
    [
        "clients",
        "groups",
        "orgs",
        "project-users",
        "projects",
        "users",
    ],
)
def test_user_commands(command):
    assert command in ls.commands
