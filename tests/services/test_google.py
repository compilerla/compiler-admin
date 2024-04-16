import sys
from tempfile import TemporaryFile

import pytest

from compiler_admin.services.google import (
    DOMAIN,
    GAM,
    GROUP_PARTNERS,
    GROUP_STAFF,
    GROUP_TEAM,
    GYB,
    USER_ARCHIVE,
    user_account_name,
    CallGAMCommand,
    CallGYBCommand,
    add_user_to_group,
    move_user_ou,
    remove_user_from_group,
    user_exists,
    user_in_group,
    user_is_partner,
    user_is_staff,
    __name__ as MODULE,
)


@pytest.fixture
def mock_gam_CallGAMCommand(mocker):
    return mocker.patch(f"{MODULE}.__CallGAMCommand")


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_user_in_group(mock_google_user_in_group):
    return mock_google_user_in_group(MODULE)


@pytest.fixture
def mock_subprocess_call(mocker):
    return mocker.patch(f"{MODULE}.subprocess.call")


def test_user_account_name_None():
    username = None
    account = user_account_name(username)

    assert account is None


def test_user_account_name_not_in_domain():
    username = "account"
    account = user_account_name(username)

    assert account == f"{username}@{DOMAIN}"


def test_user_account_name_in_domain():
    username = f"account@{DOMAIN}"
    account = user_account_name(username)

    assert username == account


def test_user_not_in_domain(capfd):
    username = "nope@anotherdomain.com"
    res = user_exists(username)
    captured = capfd.readouterr()

    assert res is False
    assert "User not in domain" in captured.out


def test_CallGAMCommand_prepends_gam(mock_gam_CallGAMCommand):
    CallGAMCommand(("args",))

    mock_gam_CallGAMCommand.assert_called_once()
    call_args = mock_gam_CallGAMCommand.call_args[0][0]
    assert call_args == (GAM, "args")


def test_CallGAMCommand_does_not_duplicate_gam(mock_gam_CallGAMCommand):
    CallGAMCommand((GAM, "args"))

    mock_gam_CallGAMCommand.assert_called_once()
    call_args = mock_gam_CallGAMCommand.call_args[0][0]
    assert call_args == (GAM, "args")


def test_CallGAMCommand_stdouterr_override(mock_gam_CallGAMCommand):
    CallGAMCommand(("args",), stdout="override-stdout", stderr="override-stderr")

    mock_gam_CallGAMCommand.assert_called_once()
    call_args = mock_gam_CallGAMCommand.call_args[0][0]
    call_str = " ".join(call_args)

    assert "redirect stdout override-stdout" in call_str
    assert "redirect stderr override-stderr" in call_str


def test_CallGYBCommand_prepends_gyb(mock_subprocess_call):
    CallGYBCommand(("args",))

    mock_subprocess_call.assert_called_once()
    call_args = mock_subprocess_call.call_args[0][0]
    assert call_args == (GYB, "args")


def test_CallGYBCommand_does_not_duplicate_gyb(mock_subprocess_call):
    CallGYBCommand((GYB, "args"))

    mock_subprocess_call.assert_called_once()
    call_args = mock_subprocess_call.call_args[0][0]
    assert call_args == (GYB, "args")


def test_CallGYBCommand_stdouterr_default(mock_subprocess_call):
    CallGYBCommand(("args",))

    mock_subprocess_call.assert_called_once()
    call_kwargs = mock_subprocess_call.call_args.kwargs

    assert "stdout" in call_kwargs
    assert call_kwargs["stdout"] == sys.stdout
    assert "stderr" in call_kwargs
    assert call_kwargs["stderr"] == sys.stderr


def test_CallGYBCommand_stdouterr_override(mock_subprocess_call):
    stdout, stderr = TemporaryFile(), TemporaryFile()
    CallGYBCommand(("args",), stdout=stdout, stderr=stderr)

    mock_subprocess_call.assert_called_once()
    call_kwargs = mock_subprocess_call.call_args.kwargs

    assert "stdout" in call_kwargs
    assert call_kwargs["stdout"] == stdout
    assert "stderr" in call_kwargs
    assert call_kwargs["stderr"] == stderr

    stdout.close()
    stderr.close()


def test_add_user_to_group(mock_google_CallGAMCommand):
    add_user_to_group("username", "thegroup")

    mock_google_CallGAMCommand.assert_called_once()


def test_move_user_ou(mock_google_CallGAMCommand):
    move_user_ou("username", "theou")

    mock_google_CallGAMCommand.assert_called_once()


def test_remove_user_from_group(mock_google_CallGAMCommand):
    remove_user_from_group("username", "thegroup")

    mock_google_CallGAMCommand.assert_called_once()


def test_user_exists_username_not_in_domain(capfd):
    res = user_exists("someone@domain.com")
    captured = capfd.readouterr()

    assert res is False
    assert "User not in domain" in captured.out


def test_user_exists_user_exists(mock_google_CallGAMCommand):
    mock_google_CallGAMCommand.return_value = 0

    res = user_exists(user_account_name("username"))

    assert res is True


def test_user_exists_user_does_not_exists(mock_google_CallGAMCommand):
    mock_google_CallGAMCommand.return_value = -1

    res = user_exists(user_account_name("username"))

    assert res is False


def test_user_in_group_user_does_not_exist(mock_google_user_exists, capfd):
    mock_google_user_exists.return_value = False

    res = user_in_group("username", "group")
    captured = capfd.readouterr()

    assert res is False
    assert "User does not exist" in captured.out


@pytest.mark.usefixtures("mock_google_CallGAMCommand")
def test_user_in_group_user_exists_in_group(mock_google_user_exists, mock_NamedTemporaryFile_with_readlines):
    mock_google_user_exists.return_value = True
    mock_NamedTemporaryFile_with_readlines(MODULE, ["group"])

    res = user_in_group("username", "group")

    assert res is True


@pytest.mark.usefixtures("mock_google_CallGAMCommand")
def test_user_in_group_user_exists_not_in_group(mock_google_user_exists, mock_NamedTemporaryFile_with_readlines):
    mock_google_user_exists.return_value = True
    mock_NamedTemporaryFile_with_readlines(MODULE, ["group"])

    res = user_in_group("username", "nope")

    assert res is False


def test_user_is_partner_checks_partner_group(mock_google_user_in_group):
    user_is_partner("username")

    mock_google_user_in_group.assert_called_once()
    assert mock_google_user_in_group.call_args.args == ("username", GROUP_PARTNERS)


def test_user_is_staff_checks_staff_group(mock_google_user_in_group):
    user_is_staff("username")

    mock_google_user_in_group.assert_called_once()
    assert mock_google_user_in_group.call_args.args == ("username", GROUP_STAFF)


@pytest.mark.e2e
def test_archive_user_exists(capfd):
    res = user_exists(USER_ARCHIVE)
    captured = capfd.readouterr()

    assert res is True
    assert f"User: {USER_ARCHIVE}" in captured.out
    assert "Google Unique ID:" in captured.out


@pytest.mark.e2e
def test_nonexistent_user_does_not_exist(capfd):
    username = f"nope_does_not_exist@{DOMAIN}"
    res = user_exists(username)
    captured = capfd.readouterr()

    assert res is False
    assert f"User: {username}, Does not exist" in captured.err


@pytest.mark.e2e
def test_nonexistent_not_in_team():
    username = f"nope_does_not_exist@{DOMAIN}"

    assert not user_in_group(username, GROUP_TEAM)


@pytest.mark.e2e
def test_archive_user_not_in_team():
    assert not user_in_group(USER_ARCHIVE, GROUP_TEAM)


@pytest.mark.e2e
def test_archive_user_is_not_partner():
    assert not user_is_partner(USER_ARCHIVE)


@pytest.mark.e2e
def test_archive_user_is_not_staff():
    assert not user_is_staff(USER_ARCHIVE)
