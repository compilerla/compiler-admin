from argparse import Namespace

from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import CallGAMCommand, user_account_name, user_exists


def signout(args: Namespace) -> int:
    """Signs the user out from all active sessions.

    Args:
        username (str): The account to sign out. Must exist already.
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    if not hasattr(args, "username"):
        raise ValueError("username is required")

    account = user_account_name(args.username)

    if not user_exists(account):
        print(f"User does not exist: {account}")
        return RESULT_FAILURE

    if getattr(args, "force", False) is False:
        cont = input(f"Signout account {account} from all active sessions? (Y/n)")
        if not cont.lower().startswith("y"):
            print("Aborting signout.")
            return RESULT_SUCCESS

    print(f"User exists, signing out from all active sessions: {account}")

    res = CallGAMCommand(("user", account, "signout"))

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
