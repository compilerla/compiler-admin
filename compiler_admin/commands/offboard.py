from tempfile import NamedTemporaryFile

from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.commands.delete import delete
from compiler_admin.commands.signout import signout
from compiler_admin.services.google import (
    USER_ARCHIVE,
    CallGAMCommand,
    CallGYBCommand,
    user_account_name,
    user_exists,
)


def offboard(username: str, alias: str = None) -> int:
    """Fully offboard a user from Compiler.

    Args:
        username (str): The user account to offboard.

        alias (str): [Optional] account to assign username as an alias
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    account = user_account_name(username)

    if not user_exists(account):
        print(f"User does not exist: {account}")
        return RESULT_FAILURE

    alias_account = user_account_name(alias)
    if alias_account is not None and not user_exists(alias_account):
        print(f"Alias target user does not exist: {alias_account}")
        return RESULT_FAILURE

    print(f"User exists, offboarding: {account}")
    res = RESULT_SUCCESS

    print("Removing from groups")
    res += CallGAMCommand(("user", account, "delete", "groups"))

    print("Backing up email")
    res += CallGYBCommand(("--service-account", "--email", account, "--action", "backup"))

    print("Starting Drive and Calendar transfer")
    res += CallGAMCommand(("create", "transfer", account, "calendar,drive", USER_ARCHIVE, "all", "releaseresources"))

    status = ""
    with NamedTemporaryFile("w+") as stdout:
        while "Overall Transfer Status: completed" not in status:
            print("Transfer in progress")
            res += CallGAMCommand(("show", "transfers", "olduser", username), stdout=stdout.name, stderr="stdout")
            status = " ".join(stdout.readlines())
            stdout.seek(0)

    res += CallGAMCommand(("user", account, "deprovision", "popimap"))

    res += signout(account)

    res += delete(account)

    if alias_account:
        print(f"Adding an alias to account: {alias_account}")
        res += CallGAMCommand(("create", "alias", account, "user", alias_account))

    print(f"Offboarding for user complete: {account}")

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
