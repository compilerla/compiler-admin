import pathlib

from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import USER_ARCHIVE, CallGYBCommand, user_account_name


def restore(username: str) -> int:
    """Restore an email backup from a prior offboarding.

    Args:
        username (str): the user account with a local email backup to restore.
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    account = user_account_name(username)
    backup_dir = f"GYB-GMail-Backup-{account}"

    if not pathlib.Path(backup_dir).exists():
        print(f"Couldn't find a local backup: {backup_dir}")
        return RESULT_FAILURE

    print(f"Found backup, starting restore process with dest: {USER_ARCHIVE} for account: {account}")

    res = CallGYBCommand(
        (
            "--service-account",
            "--email",
            USER_ARCHIVE,
            "--action",
            "restore",
            "--local-folder",
            backup_dir,
            "--label-restored",
            account,
        )
    )

    print(f"Email restore complete for: {account}")

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
