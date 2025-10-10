import pytest

from compiler_admin.commands.user import user


@pytest.mark.parametrize(
    "command",
    [
        "backupcodes",
        "convert",
        "create",
        "deactivate",
        "delete",
        "offboard",
        "reactivate",
        "reset",
        "restore",
        "signout",
    ],
)
def test_user_commands(command):
    assert command in user.commands
