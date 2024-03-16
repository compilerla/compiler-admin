from argparse import Namespace

from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import CallGAMCommand, user_account_name, user_exists


def delete(args: Namespace) -> int:
    """Delete the user account.

    Args:
        username (str): The account to delete. Must exist and not be an alias.
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    if not hasattr(args, "username"):
        raise ValueError("username is required")

    account = user_account_name(args.username)

    if not user_exists(account):
        print(f"User does not exist: {account}")
        return RESULT_FAILURE

    print(f"User exists, deleting: {account}")

    res = CallGAMCommand(("delete", "user", account, "noactionifalias"))

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
