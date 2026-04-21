import csv
import io
import json
import subprocess
import sys
from tempfile import NamedTemporaryFile
from typing import IO, Any, Sequence

# import and alias CallGAMCommand so we can simplify usage in this app
from gam import CallGAMCommand as __CallGAMCommand, initializeLogging

from compiler_admin import Format, Result

initializeLogging()

GAM = "gam"
GYB = "gyb"

# Primary domain
DOMAIN = "compiler.la"

# Org structure
OU_ALUMNI = "/alumni"
OU_CONTRACTORS = "/contractors"
OU_SERVICE_ACCOUNTS = "/service-accounts"
OU_STAFF = "/staff"
OU_PARTNERS = f"{OU_STAFF}/partners"

ORG_UNITS = dict(
    alumni=OU_ALUMNI, contractors=OU_CONTRACTORS, service_accounts=OU_SERVICE_ACCOUNTS, staff=OU_STAFF, partners=OU_PARTNERS
)


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


def get_groups(format: int = Format.BASIC, **kwargs) -> int:
    """Get information about the groups."""
    output = ""
    command = ("print", "groups")

    if len(kwargs) > 0:
        for k, v in kwargs.items():
            command += (k, v)

    if format in [Format.CSV, Format.JSON]:
        command += ("allfields",)
    if format == Format.JSON:
        command += (
            "members",
            "managers",
            "owners",
            "formatjson",
        )

    with NamedTemporaryFile("w+") as stdout:
        CallGAMCommand(command, stdout=stdout.name)
        lines = stdout.readlines()

        if format == Format.JSON:
            # GAM returns a CSV structure like "email,JSON,JSON-settings"
            # extract JSON cols to array of dicts for convenience

            # ensure we start from the CSV header
            start_index = 0
            groups_data = []
            for i, line in enumerate(lines):
                if line.startswith("email,JSON,JSON-members,JSON-settings"):
                    start_index = i
                    break

            # rebuild the clean CSV string and parse it
            clean_csv = "\n".join(lines[start_index:])
            reader = csv.DictReader(io.StringIO(clean_csv))

            for row in reader:
                # check if the JSON columns exist and have data
                if all((col in row and row[col].strip() for col in ["JSON", "JSON-members", "JSON-settings"])):
                    try:
                        # unpack the JSON strings back into native Python dicts
                        group_obj: dict = json.loads(row["JSON"])
                        group_obj["members"] = json.loads(row["JSON-members"])
                        group_obj.update(json.loads(row["JSON-settings"]))
                        groups_data.append(group_obj)
                    except json.JSONDecodeError as e:
                        print(f"Skipping row for {row.get('email')} due to JSON error: {e}")

            output = json.dumps(groups_data)
        else:
            output = "".join(lines)

    return output


def get_users(format: int = Format.BASIC, inactive: bool = False, org_units: list[str] = [], **kwargs) -> str:
    flag = str(inactive).lower()
    output = ""
    queries = ""
    command = ("print", "users", "issuspended", flag, "isarchived", flag)

    if len(kwargs) > 0:
        for k, v in kwargs.items():
            command += (k, v)

    if len(org_units) > 0:
        workspace_org_units = ORG_UNITS.values()
        if not all((ou in workspace_org_units for ou in org_units)):
            raise ValueError(f"Unexpected org_unit(s): {', '.join(org_units)}")
        queries = ",".join([f"'orgUnitPath={ou}'" for ou in org_units])
        command += ("queries", queries)

    if format == Format.CSV:
        command += ("full",)
    elif format == Format.JSON:
        queries = ",".join(org_units)
        if queries:
            user_entity = ("ous_arch" if inactive else "ou_na_ns", queries)
        else:
            user_entity = ("all", "users_arch_or_susp" if inactive else "users_na_ns")

        command = (
            "info",
            "users",
            *user_entity,
            "nobuildingnames",
            "noschemas",
            "formatjson",
        )

    with NamedTemporaryFile("w+") as stdout:
        CallGAMCommand(command, stdout=stdout.name, stderr="stdout")
        lines = stdout.readlines()
        if format == Format.JSON:
            # GAM returns JSON record lines, write a JSON array for convenience
            output = f"[{",".join(lines)}]"
        else:
            output = "".join(lines)

    return output


def get_org_units(format: int = Format.CSV) -> int:
    """Print information about the org units."""
    return CallGAMCommand(("print", "orgs"))


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
        if res != Result.SUCCESS:
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
