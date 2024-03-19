from argparse import Namespace

from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import USER_HELLO, CallGAMCommand, user_account_name, user_exists


def reset_password(args: Namespace) -> int:
    """Reset a user's password.

    Optionally notify an email address with the new randomly generated password.

    Args:
        username (str): the user account to reset.

        notify (str): an email address to send the new password notification.
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    if not hasattr(args, "username"):
        raise ValueError("username is required")

    account = user_account_name(args.username)

    if not user_exists(account):
        print(f"User does not exist: {account}")
        return RESULT_FAILURE

    command = ("update", "user", account, "password", "random")

    notify = getattr(args, "notify", None)
    if notify:
        command += ("notify", notify, "from", USER_HELLO)

    print(f"User exists, resetting password: {account}")

    res = CallGAMCommand(command)

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
