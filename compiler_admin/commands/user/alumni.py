from argparse import Namespace

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.reset import reset
from compiler_admin.services.google import (
    OU_ALUMNI,
    USER_HELLO,
    CallGAMCommand,
    move_user_ou,
    user_account_name,
    user_exists,
)


def alumni(args: Namespace) -> int:
    """Convert a user to a Compiler alumni.

    Optionally notify an email address with the new randomly generated password.

    Args:
        username (str): the user account to convert.

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

    if getattr(args, "force", False) is False:
        cont = input(f"Convert account to alumni for {account}? (Y/n)")
        if not cont.lower().startswith("y"):
            print("Aborting conversion.")
            return RESULT_SUCCESS

    res = RESULT_SUCCESS

    print("Removing from groups")
    res += CallGAMCommand(("user", account, "delete", "groups"))

    print(f"Moving to OU: {OU_ALUMNI}")
    res += move_user_ou(account, OU_ALUMNI)

    # reset password, sign out
    res += reset(args)

    print("Clearing user profile info")
    for prop in ["address", "location", "otheremail", "phone"]:
        command = ("update", "user", account, prop, "clear")
        res += CallGAMCommand(command)

    print("Resetting recovery email")
    recovery = getattr(args, "recovery_email", "")
    command = ("update", "user", account, "recoveryemail", recovery)
    res += CallGAMCommand(command)

    print("Resetting recovery phone")
    recovery = getattr(args, "recovery_phone", "")
    command = ("update", "user", account, "recoveryphone", recovery)
    res += CallGAMCommand(command)

    print("Turning off 2FA")
    command = ("user", account, "turnoff2sv")
    res += CallGAMCommand(command)

    print("Resetting email signature")
    # https://github.com/taers232c/GAMADV-XTD3/wiki/Users-Gmail-Send-As-Signature-Vacation#manage-signature
    command = (
        "user",
        account,
        "signature",
        f"Compiler LLC<br />https://compiler.la<br />{USER_HELLO}",
        "replyto",
        USER_HELLO,
        "default",
        "treatasalias",
        "false",
        "name",
        "Compiler LLC",
        "primary",
    )
    res += CallGAMCommand(command)

    return res
