import json
import re
import sys
from tempfile import TemporaryFile

import pytest

from compiler_admin import Format, Result
from compiler_admin.services.google import (
    GoogleAccount,
    GoogleArchive,
    GoogleGroups,
    GoogleOrgs,
    GoogleService,
    GoogleUsers,
    __name__ as MODULE,
)


@pytest.fixture
def get_command_str():
    def _get_command_str(mocked_gam_command):
        mocked_gam_command.assert_called_once()
        call_args = mocked_gam_command.call_args[0]
        return " ".join([str(arg) for arg in call_args[0]])

    return _get_command_str


@pytest.fixture
def mock_gam_CallGAMCommand(mocker):
    return mocker.patch(f"{MODULE}.CallGAMCommand")


@pytest.fixture
def mock_GoogleGroups(mocker):
    return mocker.patch(f"{MODULE}.GoogleGroups")


@pytest.fixture
def mock_GoogleOrgs(mocker):
    return mocker.patch(f"{MODULE}.GoogleOrgs")


@pytest.fixture
def mock_subprocess_call(mocker):
    return mocker.patch(f"{MODULE}.subprocess.call")


class TestGoogleService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.google = GoogleService()

    def test_gam_command__prepends_gam(self, mock_gam_CallGAMCommand, get_command_str):
        self.google.gam_command(("args",))

        command = get_command_str(mock_gam_CallGAMCommand)

        assert command == f"{self.google.GAM} args"

    def test_gam_command__does_not_duplicate_gam(self, mock_gam_CallGAMCommand, get_command_str):
        self.google.gam_command((self.google.GAM, "args"))

        command = get_command_str(mock_gam_CallGAMCommand)

        assert command == f"{self.google.GAM} args"

    def test_gam_command__stdouterr_override(self, mock_gam_CallGAMCommand, get_command_str):
        self.google.gam_command(("args",), stdout="override-stdout", stderr="override-stderr")

        command = get_command_str(mock_gam_CallGAMCommand)

        assert "redirect stdout override-stdout" in command
        assert "redirect stderr override-stderr" in command

    def test_gam_command_output(self, mock_gam_CallGAMCommand, mock_NamedTemporaryFile_with_readlines, get_command_str):
        expected_output = ["output"]
        mock_NamedTemporaryFile_with_readlines(MODULE, expected_output)

        output = self.google.gam_command_output(("command",))
        command = get_command_str(mock_gam_CallGAMCommand)

        assert output == expected_output
        assert "redirect stdout" in command
        assert "redirect stderr" not in command

    def test_gam_command_output__redirect_stderr(
        self, mock_gam_CallGAMCommand, mock_NamedTemporaryFile_with_readlines, get_command_str
    ):
        expected_output = ["output"]
        mock_NamedTemporaryFile_with_readlines(MODULE, expected_output)

        self.google.gam_command_output(("command",), stderr="stderr-override")
        command = get_command_str(mock_gam_CallGAMCommand)

        assert "redirect stderr stderr-override" in command

    def test_gyb_command__prepends_gyb(self, mock_subprocess_call):
        self.google.gyb_command(("args",))

        mock_subprocess_call.assert_called_once()
        call_args = mock_subprocess_call.call_args[0][0]
        assert call_args == (self.google.GYB, "args")

    def test_gyb_command__does_not_duplicate_gyb(self, mock_subprocess_call):
        self.google.gyb_command((self.google.GYB, "args"))

        mock_subprocess_call.assert_called_once()
        call_args = mock_subprocess_call.call_args[0][0]
        assert call_args == (self.google.GYB, "args")

    def test_gyb_command__stdouterr_default(self, mock_subprocess_call):
        self.google.gyb_command(("args",))

        mock_subprocess_call.assert_called_once()
        call_kwargs = mock_subprocess_call.call_args.kwargs

        assert "stdout" in call_kwargs
        assert call_kwargs["stdout"] == sys.stdout
        assert "stderr" in call_kwargs
        assert call_kwargs["stderr"] == sys.stderr

    def test_gyb_command__stdouterr_override(self, mock_subprocess_call):
        stdout, stderr = TemporaryFile(), TemporaryFile()
        self.google.gyb_command(("args",), stdout=stdout, stderr=stderr)

        mock_subprocess_call.assert_called_once()
        call_kwargs = mock_subprocess_call.call_args.kwargs

        assert "stdout" in call_kwargs
        assert call_kwargs["stdout"] == stdout
        assert "stderr" in call_kwargs
        assert call_kwargs["stderr"] == stderr

        stdout.close()
        stderr.close()


class TestGoogleAccount:

    @pytest.fixture(autouse=True)
    def setup(self, mock_gam_gyb):
        self.google = GoogleAccount("username")
        mock_gam_gyb(self.google)

    def test_init__username_None(self):
        username = None
        account = GoogleAccount(username)

        assert account.username == account.account == ""
        assert str(account) == ""

    def test_init__username_not_in_domain(self):
        username = "account"
        account = GoogleAccount(username)

        assert account == f"{username}@{GoogleAccount.DOMAIN}"

    def test_init__username_in_domain(self):
        username = f"account@{GoogleAccount.DOMAIN}"
        account = GoogleAccount(username)

        assert username == account

    def test_add_email_alias(self, get_command_str):
        alias = "alias@example.com"

        self.google.add_email_alias(alias)

        command = get_command_str(self.google.gam_command)
        assert f"create alias {alias}" in command
        assert f"user {self.google}" in command

    def test_exists__exists(self, mocker):
        mocker.patch.object(self.google, "get_info", return_value={"First Name": "Test", "Last Name": "User"})

        assert self.google.exists() is True

    def test_exists__not_exists(self, mocker):
        mocker.patch.object(self.google, "get_info", return_value={})

        assert self.google.exists() is False

    def test_get_backup_codes__user_does_not_exist(self, mock_account_exists, capfd):
        mock_account_exists(self.google, False)

        res = self.google.get_backup_codes()
        captured = capfd.readouterr()

        assert res == ""
        assert f"User does not exist: {self.google}" in captured.out

    def test_get_backup_codes__user_exists_has_codes(self, mock_account_exists):
        codes = "12345678"
        self.google.gam_command_output.return_value = codes
        mock_account_exists(self.google, True)

        res = self.google.get_backup_codes()

        assert res == codes

    def test_get_backup_codes__user_exists_no_codes(self, mock_account_exists):
        no_codes_output = "Show 0 Backup Verification Codes"
        new_codes = "87654321"
        self.google.gam_command_output.side_effect = [[no_codes_output], [new_codes]]
        mock_account_exists(self.google, True)

        assert self.google.get_backup_codes() == new_codes

    def test_get_info__exists(self, mock_NamedTemporaryFile_with_readlines):
        mock_NamedTemporaryFile_with_readlines(MODULE, ["First Name:Test", "Last Name:User"])
        self.google.gam_command.return_value = Result.SUCCESS

        res = self.google.get_info()

        assert res == {"First Name": "Test", "Last Name": "User"}

    def test_get_info__not_exists(self):
        self.google.gam_command.return_value = Result.FAILURE

        res = self.google.get_info()

        assert res == {}

    def test_is_deactivated__checks_alumni_ou(self, mock_GoogleOrgs):
        self.google.is_deactivated()

        mock_GoogleOrgs.assert_called_once_with(mock_GoogleOrgs.OU_ALUMNI)
        mock_GoogleOrgs.return_value.contains_user.assert_called_once_with(self.google)

    def test_is_partner__checks_partner_group(self, mock_GoogleGroups):
        self.google.is_partner()

        mock_GoogleGroups.assert_called_once_with(mock_GoogleGroups.GROUP_PARTNERS)
        mock_GoogleGroups.return_value.contains_user.assert_called_once_with(self.google)

    def test_is_staff__checks_staff_group(self, mock_GoogleGroups):
        self.google.is_staff()

        mock_GoogleGroups.assert_called_once_with(mock_GoogleGroups.GROUP_STAFF)
        mock_GoogleGroups.return_value.contains_user.assert_called_once_with(self.google)


class TestGoogleArchive:
    @pytest.fixture(autouse=True)
    def setup(self, mock_gam_gyb):
        self.account = GoogleAccount("username")
        self.google = GoogleArchive()
        mock_gam_gyb(self.google)

    def test_archive_content(self, get_command_str):
        self.google.archive_content(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"create transfer {self.account}" in command
        assert "calendar,drive" in command
        assert str(GoogleUsers.USER_ARCHIVE) in command
        assert "releaseresources" in command

    def test_await_archive_completion(self, mocker):
        self.google.gam_command_output.side_effect = [["Overall Transfer Status: completed"]]

        self.google.await_archive_completion(self.account)

        assert self.google.gam_command_output.call_count == 1

    def test_await_archive_completion__callback(self, mocker):
        callback = mocker.Mock()
        self.google.gam_command_output.side_effect = [
            ["Overall Transfer Status: pending"],
            ["Overall Transfer Status: completed"],
        ]

        self.google.await_archive_completion(self.account, callback=callback)

        assert self.google.gam_command_output.call_count == 2
        assert mocker.call("", "Overall Transfer Status: pending") in callback.mock_calls
        assert mocker.call("Overall Transfer Status: pending", "Overall Transfer Status: completed") in callback.mock_calls

    def test_create_email_backup(self, get_command_str):
        self.google.create_email_backup(self.account)

        command = get_command_str(self.google.gyb_command)
        assert "--service-account" in command
        assert f"--email {self.account}" in command
        assert "--action backup" in command

    def test_restore_email_backup(self, get_command_str):
        self.google.restore_email_backup(self.account, "/backupdir")

        command = get_command_str(self.google.gyb_command)
        assert "--service-account" in command
        assert f"--email {GoogleUsers.USER_ARCHIVE}" in command
        assert "--action restore" in command
        assert "--local-folder /backupdir" in command
        assert f"--label-restored {self.account}" in command


class TestGoogleGroups:
    @pytest.fixture(autouse=True)
    def setup(self, mock_gam_gyb):
        self.account = GoogleAccount("username")
        self.group = GoogleAccount("group")
        self.google = GoogleGroups(self.group)
        mock_gam_gyb(self.google)

    def test_add_user(self, get_command_str):
        self.google.add_user(self.account)

        command = get_command_str(self.google.gam_command)

        assert f"user {self.account}" in command
        assert f"add groups member {self.group}" in command

    def test_contains_user__user_does_not_exist(self, mock_account_exists):
        mock_account_exists(self.account, False)

        assert self.google.contains_user(self.account) is False

    def test_contains_user__user_exists_in_group(self, mock_account_exists):
        mock_account_exists(self.account, True)
        self.google.gam_command_output.return_value = [str(self.group)]

        assert self.google.contains_user(self.account) is True

    def test_contains_user__user_exists_not_in_group(self, mock_account_exists):
        mock_account_exists(self.account, True)
        self.google.gam_command_output.return_value = [str(self.group)]

        assert self.google.contains_user(self.account, group=GoogleAccount("nope")) is False

    def test_get(self, get_command_str):
        self.google.get()

        command = get_command_str(self.google.gam_command_output)

        assert "print groups" in command

    def test_get__kwargs(self, get_command_str):
        self.google.get(kwarg1="value1")

        command = get_command_str(self.google.gam_command_output)

        assert "kwarg1 value1" in command

    def test_get__format_csv(self, get_command_str):
        self.google.get(format=Format.CSV)

        command = get_command_str(self.google.gam_command_output)

        assert "allfields" in command

    def test_get__format_json(self, get_command_str):
        expected = json.dumps(
            [
                {
                    "json": "json_value",
                    "members": [{"json-members": "json_members_value"}],
                    "json-settings": "json_settings_value",
                }
            ]
        )

        self.google.gam_command_output.return_value = [
            "# comment, blank line, should be skipped",
            "email,JSON,JSON-members,JSON-settings",
            'example@example.com,"{""json"":""json_value""}","[{""json-members"":""json_members_value""}]","{""json-settings"":""json_settings_value""}",',  # noqa: E501
        ]

        output = self.google.get(format=Format.JSON)
        command = get_command_str(self.google.gam_command_output)

        assert "allfields" in command
        assert "members managers owners" in command
        assert "formatjson" in command
        assert output == expected

    def test_get__format_json__bad_encoding(self):
        self.google.gam_command_output.return_value = [
            "email,JSON,JSON-members,JSON-settings",
            "example@example.com,not-json,not-json,not-json",
        ]

        output = self.google.get(format=Format.JSON)

        assert output == "[]"

    def test_get__format_json__missing_data(self):
        self.google.gam_command_output.return_value = [
            "email,JSON,JSON-members,JSON-settings",
            "example@example.com,,,",
        ]

        output = self.google.get(format=Format.JSON)

        assert output == "[]"

    def test_get__format_json__no_data(self):
        self.google.gam_command_output.return_value = []

        output = self.google.get(format=Format.JSON)

        assert output == "[]"

    def test_remove_user(self, get_command_str):
        self.google.remove_user(self.account)

        command = get_command_str(self.google.gam_command)

        assert f"update group {self.group}" in command
        assert f"delete {self.account}" in command


class TestGoogleOrgs:
    @pytest.fixture(autouse=True)
    def setup(self, mock_gam_gyb):
        self.account = GoogleAccount("username")
        self.ou = GoogleOrgs.OU_SERVICE_ACCOUNTS
        self.google = GoogleOrgs(self.ou)
        mock_gam_gyb(self.google)

    @pytest.mark.parametrize("ou_key", GoogleOrgs.ORG_UNITS.keys())
    def test_get_item(self, ou_key):
        assert self.google[ou_key] == self.google.ORG_UNITS[ou_key]

    def test_contains_user__unexepected_ou(self):
        with pytest.raises(ValueError, match="Unexpected OU: /unexpected"):
            self.google.contains_user(self.account, "/unexpected")

    def test_contains_user__user_does_not_exist(self, mock_account_exists):
        mock_account_exists(self.account, False)

        assert self.google.contains_user(self.account, self.ou) is False

    def test_contains_user__user_exists_in_ou(self, mock_account_exists):
        mock_account_exists(self.account, True)
        self.google.gam_command_output.return_value = [str(self.account)]

        assert self.google.contains_user(self.account, self.ou) is True

    def test_contains_user__user_exists_not_in_ou(self, mock_account_exists):
        mock_account_exists(self.account, True)
        self.google.gam_command_output.return_value = ["nope"]

        assert self.google.contains_user(self.account, self.ou) is False

    def test_get(self, get_command_str):
        self.google.get()

        command = get_command_str(self.google.gam_command_output)

        assert "print orgs" in command

    def test_get__kwargs(self, get_command_str):
        self.google.get(kwarg1="value1")

        command = get_command_str(self.google.gam_command_output)

        assert "kwarg1 value1" in command

    def test_move_user(self):
        self.google.move_user(self.account, self.ou)

        self.google.gam_command.assert_called_once()

    def test_move_user__unexpected_ou(self):
        with pytest.raises(ValueError, match="Unexpected OU: /unexpected"):
            self.google.move_user(self.account, "/unexpected")


class TestGoogleUsers:
    @pytest.fixture(autouse=True)
    def setup(self, mock_gam_gyb):
        self.account = GoogleAccount("username")
        self.google = GoogleUsers()
        mock_gam_gyb(self.google)

    def test_clear_profile(self, mocker):
        self.google.clear_profile(self.account)

        for prop in ["address", "location", "otheremail", "phone"]:
            assert mocker.call(("update", "user", self.account, prop, "clear")) in self.google.gam_command.mock_calls

    def test_create(self, get_command_str):
        self.google.create(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"create user {self.account}" in command
        assert "password random" in command
        assert "changepassword" in command

    def test_create__notify(self, get_command_str):
        self.google.create(self.account, notify="notify@example.com")

        command = get_command_str(self.google.gam_command)
        assert "notify notify@example.com" in command
        assert f"from {GoogleUsers.USER_HELLO}" in command

    def test_delete(self, get_command_str):
        self.google.delete(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"delete user {self.account}" in command
        assert "noactionifalias" in command

    def test_deprovision_popimap(self, get_command_str):
        self.google.deprovision_popimap(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"user {self.account}" in command
        assert "deprovision popimap" in command

    def test_disable_2fa(self, get_command_str):
        self.google.disable_2fa(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"user {self.account}" in command
        assert "turnoff2sv" in command

    def test_get(self, get_command_str):
        self.google.get(kwarg1="one")

        command = get_command_str(self.google.gam_command_output)

        assert "print users" in command
        assert "issuspended false isarchived false" in command
        assert "kwarg1 one" in command

    def test_get__inactive(self, get_command_str):
        self.google.get(inactive=True)

        command = get_command_str(self.google.gam_command_output)

        assert "issuspended true isarchived true" in command

    def test_get__format_csv(self, get_command_str):
        self.google.get(format=Format.CSV)

        command = get_command_str(self.google.gam_command_output)

        assert "full" in command

    @pytest.mark.parametrize("inactive,expected_in_command", ((True, "users_arch_or_susp"), (False, "users_na_ns")))
    def test_get__format_json(self, get_command_str, inactive, expected_in_command):
        self.google.get(inactive=inactive, format=Format.JSON)

        command = get_command_str(self.google.gam_command_output)

        assert "info users all" in command
        assert "formatjson" in command
        assert expected_in_command in command

    def test_get__org_units(self, get_command_str):
        self.google.get(org_units=GoogleOrgs.ORG_UNITS.values())

        command = get_command_str(self.google.gam_command_output)

        assert "queries" in command
        for ou in GoogleOrgs.ORG_UNITS.values():
            assert f"'orgUnitPath={ou}'" in command

    def test_get__org_units_unexepected(self):
        with pytest.raises(ValueError, match=re.escape("Unexpected org_unit(s): /unexpected")):
            self.google.get(org_units=["/unexpected"])

    @pytest.mark.parametrize("inactive,ou_entity", [(True, "ous_arch"), (False, "ou_na_ns")])
    def test_get__org_units__format_json(self, get_command_str, inactive, ou_entity):
        self.google.get(inactive=inactive, org_units=GoogleOrgs.ORG_UNITS.values(), format=Format.JSON)

        command = get_command_str(self.google.gam_command_output)

        assert ou_entity in command

    def test_reset_recovery_info(self, mocker):
        self.google.reset_recovery_info(self.account, recovery_email="email@example.com", recovery_phone="555-555-5555")

        assert (
            mocker.call(("update", "user", self.account, "recoveryemail", "email@example.com"))
            in self.google.gam_command.mock_calls
        )
        assert (
            mocker.call(("update", "user", self.account, "recoveryphone", "555-555-5555"))
            in self.google.gam_command.mock_calls
        )

    def test_reset_password(self, get_command_str):
        self.google.reset_password(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"update user {self.account} password random" in command
        assert "changepassword" in command

    def test_reset_password__notify(self, get_command_str):
        self.google.reset_password(self.account, notify="notify@example.com")

        command = get_command_str(self.google.gam_command)
        assert f"notify notify@example.com from {GoogleUsers.USER_HELLO}" in command

    def test_remove_from_groups(self, get_command_str):
        self.google.remove_from_groups(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"user {self.account}" in command
        assert "delete groups" in command

    def test_signout(self, get_command_str):
        self.google.signout(self.account)

        command = get_command_str(self.google.gam_command)
        assert f"user {self.account} signout" in command


@pytest.mark.e2e
class TestE2E:

    def test_archive_user_exists(self, capfd):
        res = GoogleAccount(GoogleUsers.USER_ARCHIVE).exists()
        captured = capfd.readouterr()

        assert res is True
        assert f"User: {GoogleUsers.USER_ARCHIVE}" in captured.out
        assert "Google Unique ID:" in captured.out

    def test_nonexistent_user_does_not_exist(self, capfd):
        username = f"nope_does_not_exist@{GoogleAccount.DOMAIN}"
        res = GoogleAccount(username).exists()
        captured = capfd.readouterr()

        assert res is False
        assert f"User: {username}, Does not exist" in captured.err

    def test_nonexistent_not_in_team(self):
        username = f"nope_does_not_exist@{GoogleAccount.DOMAIN}"

        assert not GoogleGroups(GoogleGroups.GROUP_TEAM).contains_user(username)

    def test_archive_user_not_in_team(self):
        assert not GoogleGroups(GoogleGroups.GROUP_TEAM).contains_user(GoogleUsers.USER_ARCHIVE)

    def test_archive_user_is_not_partner(self):
        assert not GoogleUsers.USER_ARCHIVE.is_partner()

    def test_archive_user_is_not_staff(self):
        assert not GoogleUsers.USER_ARCHIVE.is_staff()
