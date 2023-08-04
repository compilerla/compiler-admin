from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import CallGAMCommand, user_account_name, user_exists


def signout(username: str) -> int:
    """Signs the user out from all active sessions.

    Args:
        username (str): The account to sign out. Must exist already.
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    account = user_account_name(username)

    if not user_exists(account):
        print(f"User does not exist: {account}")
        return RESULT_FAILURE

    print(f"User exists, signing out from all active sessions: {account}")

    res = CallGAMCommand(("user", account, "signout"))

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
