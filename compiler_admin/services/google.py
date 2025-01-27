import subprocess
import sys
from tempfile import NamedTemporaryFile
from typing import Any, Sequence, IO

from compiler_admin import RESULT_SUCCESS

# import and alias CallGAMCommand so we can simplify usage in this app
from gam import CallGAMCommand as __CallGAMCommand, initializeLogging

initializeLogging()

GAM = "gam"
GYB = "gyb"

# Primary domain
DOMAIN = "compiler.la"

# Org structure
OU_ALUMNI = "alumni"
OU_CONTRACTORS = "contractors"
OU_STAFF = "staff"
OU_PARTNERS = f"{OU_STAFF}/partners"


def user_account_name(username: str) -> str:
    """Return the full user account in the Compiler domain.

    Args:
        username (str): The username sans domain of a Compiler account.
    Returns:
        username@compiler.la
    """
    if username is None:
        return None
    if username.endswith(f"@{DOMAIN}"):
        return username
    return f"{username}@{DOMAIN}"


# Archive account
USER_ARCHIVE = user_account_name("archive")

# Hello account
USER_HELLO = user_account_name("hello")

# Groups
GROUP_PARTNERS = user_account_name("partners")
GROUP_STAFF = user_account_name("staff")
GROUP_TEAM = user_account_name("team")


def CallGAMCommand(args: Sequence[str], stdout: str = None, stderr: str = None) -> int:
    """Call GAM with the provided arguments, optionally redirecting stdout and/or stderr."""
    if stdout:
        args = ("redirect", "stdout", stdout, *args)

    if stderr:
        args = ("redirect", "stderr", stderr, *args)

    if not args[0] == GAM:
        args = (GAM, *args)

    return int(__CallGAMCommand(args))


def CallGYBCommand(args: Sequence[str], stdout: IO[Any] = sys.stdout, stderr: IO[Any] = sys.stderr) -> int:
    """Call GYB with the provided arguments."""
    if not args[0] == GYB:
        args = (GYB, *args)

    return subprocess.call(args, stdout=stdout, stderr=stderr)


def add_user_to_group(username: str, group: str) -> int:
    """Add a user to a group."""
    return CallGAMCommand(("user", username, "add", "groups", "member", group))


def get_backup_codes(username: str) -> str:
    if not user_exists(username):
        print(f"User does not exist: {username}")
        return ""

    output = ""
    command = ("user", username, "show", "backupcodes")
    with NamedTemporaryFile("w+") as stdout:
        CallGAMCommand(command, stdout=stdout.name, stderr="stdout")
        output = "".join(stdout.readlines())

    if "Show 0 Backup Verification Codes" in output:
        command = ("user", username, "update", "backupcodes")
        with NamedTemporaryFile("w+") as stdout:
            CallGAMCommand(command, stdout=stdout.name, stderr="stdout")
            output = "".join(stdout.readlines())

    return output


def move_user_ou(username: str, ou: str) -> int:
    """Move a user into a new OU."""
    return CallGAMCommand(("update", "ou", ou, "move", username))


def remove_user_from_group(username: str, group: str) -> int:
    """Remove a user from a group."""
    return CallGAMCommand(("update", "group", group, "delete", username))


def user_exists(username: str) -> bool:
    """Checks if a user exists.

    Args:
        username (str): The user@compiler.la to check for existence.
    Returns:
        True if the user exists. False otherwise.
    """
    if not str(username).endswith(DOMAIN):
        print(f"User not in domain: {username}")
        return False

    info = user_info(username)

    return info != {}


def user_info(username: str) -> dict:
    """Get a dict of basic user information.

    Args:
        username (str): The user@compiler.la to get.
    Returns:
        A dict of user information
    """
    if not str(username).endswith(DOMAIN):
        print(f"User not in domain: {username}")
        return {}

    with NamedTemporaryFile("w+") as stdout:
        res = CallGAMCommand(("info", "user", username, "quick"), stdout=stdout.name)
        if res != RESULT_SUCCESS:
            # user doesn't exist
            return {}
        # user exists, read data
        lines = stdout.readlines()
        # split on newline and filter out lines that aren't line "Key:Value" and empty value lines like "Key:<empty>"
        lines = [L.strip() for L in lines if len(L.split(":")) == 2 and L.split(":")[1].strip()]
        # make a map by splitting the lines, trimming key and value
        info = {}
        for line in lines:
            k, v = line.split(":")
            info[k.strip()] = v.strip()
        return info


def user_in_group(username: str, group: str) -> bool:
    """Checks if a user is in a group.

    Args:
        username (str): The user@compiler.la to check for membership in the group.
        group (str): The group@compiler.la to check for username's membership.
    Returns:
        True if the user is a member of the group. False otherwise.
    """
    if user_exists(username):
        with NamedTemporaryFile("w+") as stdout:
            CallGAMCommand(("print", "groups", "member", username), stdout=stdout.name, stderr="stdout")
            output = "\n".join(stdout.readlines())

        return group in output
    else:
        print(f"User does not exist: {username}")
        return False


def user_in_ou(username: str, ou: str) -> bool:
    """Checks if a user is in an OU.

    Args:
        username (str): The user@compiler.la to check for membership in the group.
        ou (str): The name of an OU to check for username's membership.
    Returns:
        True if the user is a member of the OU. False otherwise.
    """
    if user_exists(username):
        with NamedTemporaryFile("w+") as stdout:
            CallGAMCommand(("info", "ou", ou), stdout=stdout.name, stderr="stdout")
            output = "\n".join(stdout.readlines())
        return username in output
    else:
        print(f"User does not exist: {username}")
        return False


def user_is_deactivated(username: str) -> bool:
    """Checks if a user is in an OU.

    Args:
        username (str): The user@compiler.la to check for membership in the group.
        ou (str): The name of an OU to check for username's membership.
    Returns:
        True if the user is a member of the OU. False otherwise.
    """
    return user_in_ou(username, OU_ALUMNI)


def user_is_partner(username: str) -> bool:
    """Checks if a user is a Compiler Partner.

    Args:
        username (str): The user@compiler.la to check for partner status.
    Returns:
        True if the user is a Partner. False otherwise.
    """
    return user_in_group(username, GROUP_PARTNERS)


def user_is_staff(username: str) -> bool:
    """Checks if a user is a Compiler Staff.

    Args:
        username (str): The user@compiler.la to check for staff status.
    Returns:
        True if the user is a Staff. False otherwise.
    """
    return user_in_group(username, GROUP_STAFF)
