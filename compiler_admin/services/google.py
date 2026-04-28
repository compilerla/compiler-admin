import csv
import io
import json
import subprocess
import sys
from tempfile import NamedTemporaryFile
from typing import IO, Any, Callable, Sequence

from gam import CallGAMCommand, initializeLogging

from compiler_admin import Format, Result

initializeLogging()


class GoogleService:
    GAM = "gam"
    GYB = "gyb"

    def gam_command(self, args: Sequence[str], stdout: str = None, stderr: str = None) -> int:
        """Call GAM with the provided arguments, optionally redirecting stdout and/or stderr."""
        if stdout:
            args = ("redirect", "stdout", stdout, *args)

        if stderr:
            args = ("redirect", "stderr", stderr, *args)

        if not args[0] == self.GAM:
            args = (self.GAM, *args)

        # convert all args to str to ensure proper GAM calling
        args = tuple(str(a) for a in args)

        return int(CallGAMCommand(args))

    def gam_command_output(self, args: Sequence[str], stderr: str = None) -> list[str]:
        """Call GAM with the provided arguments, optionally redirecting stderr. Returns stdout lines as a list of str."""
        with NamedTemporaryFile("w+") as stdout:
            self.gam_command(args, stdout=stdout.name, stderr=stderr)
            return stdout.readlines()

    def gyb_command(self, args: Sequence[str], stdout: IO[Any] = sys.stdout, stderr: IO[Any] = sys.stderr) -> int:
        """Call GYB with the provided arguments."""
        if not args[0] == self.GYB:
            args = (self.GYB, *args)

        # convert all args to str to ensure proper GYB calling
        args = tuple(str(a) for a in args)

        return subprocess.call(args, stdout=stdout, stderr=stderr)


class GoogleAccount(GoogleService):
    """Models a user account in the Compiler domain."""

    DOMAIN = "compiler.la"

    def __init__(self, username: str):
        self.username = username or ""
        if self.username:
            self.account = username if username.endswith(f"@{self.DOMAIN}") else f"{username}@{self.DOMAIN}"
        else:
            self.account = ""

    def __eq__(self, value):
        return str(self) == value

    def __str__(self):
        return self.account

    def add_email_alias(self, alias: str) -> int:
        """Add a new email alias for this account.

        Args:
            alias (str): The user@compiler.la to add as an email alias for this account.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("create", "alias", alias, "user", self)
        self.gam_command(command)

    def exists(self) -> bool:
        """Checks if an account exists.

        Returns:
            True if the account exists. False otherwise.
        """
        return self.get_info() != {}

    def get_backup_codes(self) -> str:
        """Gets an account's backup codes, refreshing if needed.

        Returns:
            (str): The backup code output.
        """
        if not self.exists():
            print(f"User does not exist: {self}")
            return ""

        command = ("user", self, "show", "backupcodes")
        output = "".join(self.gam_command_output(command))

        if "Show 0 Backup Verification Codes" in output:
            command = ("user", self, "update", "backupcodes")
            output = "".join(self.gam_command_output(command))

        return output

    def get_info(self) -> dict:
        """Get a dict of basic user information.

        Args:
            account (GoogleAccount): The user@compiler.la to check for existence.

        Returns:
            (dict): The user's information.
        """
        with NamedTemporaryFile("w+") as stdout:
            res = self.gam_command(("info", "user", str(self), "quick"), stdout=stdout.name)
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

    def is_deactivated(self) -> bool:
        """Checks if the account is deactivated.

        Returns:
            True if the user is deactivated. False otherwise.
        """
        return GoogleOrgs(GoogleOrgs.OU_ALUMNI).contains_user(self)

    def is_partner(self) -> bool:
        """Checks if the account is a Compiler Partner.

        Returns:
            True if the user is a Partner. False otherwise.
        """
        return GoogleGroups(GoogleGroups.GROUP_PARTNERS).contains_user(self)

    def is_staff(self) -> bool:
        """Checks if an account is a Compiler Staff.

        Returns:
            True if the user is a Staff. False otherwise.
        """
        return GoogleGroups(GoogleGroups.GROUP_STAFF).contains_user(self)


class GoogleArchive(GoogleService):
    def archive_content(self, account: GoogleAccount) -> int:
        """DESTRUCTIVE! Archive this account's Calendar and Drive content.

        Args:
            account (GoogleAccount): The account with content to archive.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("create", "transfer", account, "calendar,drive", GoogleUsers.USER_ARCHIVE, "all", "releaseresources")
        return self.gam_command(command)

    def await_archive_completion(self, account: GoogleAccount, callback: Callable[[str, str], None] = None) -> int:
        status = ""
        command = ("show", "transfers", "olduser", account)

        while "Overall Transfer Status: completed" not in status:
            pre_status = status
            status = " ".join(self.gam_command_output(command, stderr="stdout"))
            if callback:
                callback(pre_status, status)

    def create_email_backup(self, account: GoogleAccount) -> int:
        """Create a backup of the account's email.

        Args:
            account (GoogleAccount): The account to create an email backup.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("--service-account", "--email", account, "--action", "backup")
        return self.gyb_command(command)

    def restore_email_backup(self, account: GoogleAccount, backup_dir: str) -> int:
        """Restore a backup of the account's email.

        Args:
            account (GoogleAccount): The account to create an email backup.
            backup_dir (str): The path to a directory containing the account's email backup.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = (
            "--service-account",
            "--email",
            GoogleUsers.USER_ARCHIVE,
            "--action",
            "restore",
            "--local-folder",
            backup_dir,
            "--label-restored",
            account,
        )
        return self.gyb_command(command)


class GoogleGroups(GoogleService):

    GROUP_PARTNERS = GoogleAccount("partners")
    GROUP_STAFF = GoogleAccount("staff")
    GROUP_TEAM = GoogleAccount("team")

    def __init__(self, group: GoogleAccount = None):
        self._group = group

    def add_user(self, account: GoogleAccount, group: GoogleAccount = None):
        """Add a user to a group.

        Args:
            account (GoogleAccount): The user@compiler.la to add.
            group (GoogleAccount): The group@compiler.la to add the account to.
        """
        group = group or self._group
        return self.gam_command(("user", account, "add", "groups", "member", group))

    def contains_user(self, account: GoogleAccount, group: GoogleAccount = None) -> bool:
        """Checks if the account is in a group.

        Args:
            account (GoogleAccount): The user@compiler.la to check for group membership.
            group (GoogleAccount): The group@compiler.la to check for account's membership.

        Returns:
            True if the user is a member of the group. False otherwise.
        """
        group = group or self._group
        command = ("print", "groups", "member", account)
        output = "".join(self.gam_command_output(command))
        return str(group) in output

    def get(self, format: int = Format.BASIC, **kwargs) -> int:
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

        lines = self.gam_command_output(command)
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

    def remove_user(self, account: GoogleAccount, group: GoogleAccount = None):
        """Remove a user from a group."""
        group = group or self._group
        return self.gam_command(("update", "group", group, "delete", account))


class GoogleOrgs(GoogleService):
    OU_ALUMNI = "/alumni"
    OU_CONTRACTORS = "/contractors"
    OU_SERVICE_ACCOUNTS = "/service-accounts"
    OU_STAFF = "/staff"
    OU_PARTNERS = f"{OU_STAFF}/partners"

    ORG_UNITS = dict(
        alumni=OU_ALUMNI,
        contractors=OU_CONTRACTORS,
        service_accounts=OU_SERVICE_ACCOUNTS,
        staff=OU_STAFF,
        partners=OU_PARTNERS,
    )

    def __init__(self, ou: str = None):
        self._ou = ou

    def __getitem__(self, key):
        return self.ORG_UNITS.get(key)

    def contains_user(self, account: GoogleAccount, ou: str = None) -> bool:
        """Checks if the account is in an OU.

        Args:
            account (GoogleAccount): The user@compiler.la to check for membership.
            ou (str): The name of an OU to check for account's membership.

        Returns:
            True if the account is a member of the OU. False otherwise.
        """
        ou = ou or self._ou

        if ou not in self.ORG_UNITS.values():
            raise ValueError(f"Unexpected OU: {ou}")

        command = ("info", "ou", ou)
        output = "".join(self.gam_command_output(command))
        return str(account) in output

    def get(self, **kwargs) -> str:
        """Print information about the org units."""
        command = ("print", "orgs")

        if len(kwargs) > 0:
            for k, v in kwargs.items():
                command += (k, v)

        return "".join(self.gam_command_output(command))

    def move_user(self, account: GoogleAccount, ou: str = None) -> int:
        """Move an account into a new OU."""
        ou = ou or self._ou

        if ou not in self.ORG_UNITS.values():
            raise ValueError(f"Unexpected OU: {ou}")

        return self.gam_command(("update", "ou", ou, "move", account))


class GoogleUsers(GoogleService):
    """Interact with users in the Compiler domain."""

    # Archive account
    USER_ARCHIVE = GoogleAccount("archive")
    # Hello account
    USER_HELLO = GoogleAccount("hello")

    def clear_profile(self, account: GoogleAccount) -> int:
        """DESTRUCTIVE! Clears user account profile info.

        Args:
            account (GoogleAccount): The user@compiler.la whose profile to clear.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        for prop in ["address", "location", "otheremail", "phone"]:
            command = ("update", "user", account, prop, "clear")
            self.gam_command(command)

    def create(self, account: GoogleAccount, notify: str = None, *args):
        command = ("create", "user", account, "password", "random", "changepassword")
        if notify:
            command += ("notify", notify, "from", self.USER_HELLO)
        command += (*args,)

        return self.gam_command(command)

    def delete(self, account: GoogleAccount) -> int:
        """DESTRUCTIVE! Deletes an account.

        Args:
            account (GoogleAccount): The user@compiler.la to delete.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("delete", "user", account, "noactionifalias")
        return self.gam_command(command)

    def deprovision_popimap(self, account: GoogleAccount) -> int:
        """DESTRUCTIVE! Deprovisions POP/IMAP (email services) for the account.

        Args:
            account (GoogleAccount): The user@compiler.la to deprovision POP/IMAP for.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("user", account, "deprovision", "popimap")
        return self.gam_command(command)

    def disable_2fa(self, account: GoogleAccount) -> int:
        """DESTRUCTIVE! Disables 2FA on the account.

        Args:
            account (GoogleAccount): The user@compiler.la to disable 2FA for.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("user", account, "turnoff2sv")
        return self.gam_command(command)

    def get(self, format: int = Format.BASIC, inactive: bool = False, org_units: list[str] = [], **kwargs) -> str:
        """Get a list of accounts in the workspace.

        Args:
            format (int): The format for the output. Use the `compiler_admin.Format` helper class.
            inactive (bool): True to display inactive users. False to display active users.
            org_units (list[str]): A list of org units that, if provided, filters users to only those in any of the org units.

        Returns:
            str: A formatted list of user accounts.
        """
        flag = str(inactive).lower()
        output = ""
        queries = ""
        command = ("print", "users", "issuspended", flag, "isarchived", flag)

        if len(kwargs) > 0:
            for k, v in kwargs.items():
                command += (k, v)

        if len(org_units) > 0:
            workspace_org_units = GoogleOrgs.ORG_UNITS.values()
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

        lines = self.gam_command_output(command)
        if format == Format.JSON:
            # GAM returns JSON record lines, write a JSON array for convenience
            output = f"[{",".join(lines)}]"
        else:
            output = "".join(lines)

        return output

    def reset_recovery_info(self, account: GoogleAccount, recovery_email: str, recovery_phone: str) -> int:
        """DESTRUCTIVE! Resets the account's recovery information.

        Args:
            account (GoogleAccount): The user@compiler.la to reset recovery info for.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("update", "user", account, "recoveryemail", recovery_email)
        res = self.gam_command(command)

        command = ("update", "user", account, "recoveryphone", recovery_phone)
        res += self.gam_command(command)

        return res

    def reset_password(self, account: GoogleAccount, notify: str = None) -> int:
        """DESTRUCTIVE! Resets the account's password to a new, random password.

        Args:
            account (GoogleAccount): The user@compiler.la to reset the password for.
            notify (str): Optional email address to send a notification with the new password.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("update", "user", account, "password", "random", "changepassword")
        if notify:
            command += ("notify", notify, "from", GoogleUsers.USER_HELLO)

        self.gam_command(command)

    def remove_from_groups(self, account: GoogleAccount) -> int:
        """DESTRUCTIVE! Removes the account from all groups.

        Args:
            account (GoogleAccount): The user@compiler.la to remove from all its groups.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("user", account, "delete", "groups")
        return self.gam_command(command)

    def signout(self, account: GoogleAccount) -> int:
        """Sign a user out from all active sessions.

        Args:
            account (GoogleAccount): The user@compiler.la to sign out.

        Returns:
            int: A code indicating if the operation succeeded or failed.
        """
        command = ("user", account, "signout")
        return self.gam_command(command)
