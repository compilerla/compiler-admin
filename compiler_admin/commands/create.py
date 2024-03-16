from argparse import Namespace
from typing import Sequence

from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import GROUP_TEAM, add_user_to_group, CallGAMCommand, user_account_name, user_exists


def create(args: Namespace, *extra: Sequence[str]) -> int:
    """Create a new user account in Compiler.

    The user's password is randomly generated and requires reset on first login.

    Extra args are passed along to GAM as options.
    See https://github.com/taers232c/GAMADV-XTD3/wiki/Users#create-a-user
    for the complete list of options supported.

    Args:
        username (str): The account to create. Must not exist already.
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    if not hasattr(args, "username"):
        raise ValueError("username is required")

    account = user_account_name(args.username)

    if user_exists(account):
        print(f"User already exists: {account}")
        return RESULT_FAILURE

    print(f"User does not exist, continuing: {account}")

    res = CallGAMCommand(("create", "user", account, "password", "random", "changepassword", *extra))

    res += add_user_to_group(account, GROUP_TEAM)

    print(f"User created successfully: {account}")

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
