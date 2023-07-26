from tempfile import NamedTemporaryFile
from typing import Sequence

# import and alias CallGAMCommand so we can simplify usage in this app
from gam import CallGAMCommand as __CallGAMCommand, initializeLogging

initializeLogging()

GAM = "gam"

# Primary domain
DOMAIN = "compiler.la"

# Org structure
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

# Groups
GROUP_PARTNERS = user_account_name("partners")
GROUP_STAFF = user_account_name("staff")
GROUP_TEAM = user_account_name("team")


def CallGAMCommand(args: Sequence[str]) -> int:
    """Call GAM with the provided arguments."""
    if not args[0] == GAM:
        args = (GAM, *args)

    return int(__CallGAMCommand(args))


def CallGAMCommand_RedirectOutErr(args: Sequence[str], stdout: str = None, stderr: str = None) -> int:
    """Call GAM with the provided arguments, optionally redirecting stdout and/or stderr."""
    if stdout:
        args = ("redirect", "stdout", stdout, *args)

    if stderr:
        args = ("redirect", "stderr", stderr, *args)

    return CallGAMCommand(args)


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

    res = CallGAMCommand(("info", "user", username, "quick"))

    return res == 0


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
            CallGAMCommand_RedirectOutErr(("print", "groups", "member", username), stdout=stdout.name, stderr="stdout")
            output = "\n".join(stdout.readlines())

        return group in output
    else:
        print(f"User does not exist: {username}")
        return False


def user_is_partner(username: str) -> bool:
    return user_in_group(username, GROUP_PARTNERS)


def user_is_staff(username: str) -> bool:
    return user_in_group(username, GROUP_STAFF)


def add_user_to_group(username: str, group: str) -> bool:
    """Add a user to a group."""
    return bool(CallGAMCommand(("user", username, "add", "groups", "member", group)))
