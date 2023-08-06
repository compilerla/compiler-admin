import pytest

from compiler_admin.services.google import (
    DOMAIN,
    GAM,
    GROUP_TEAM,
    USER_ARCHIVE,
    user_account_name,
    CallGAMCommand,
    user_exists,
    user_in_group,
    user_is_partner,
    user_is_staff,
)


@pytest.fixture
def mock_gam_CallGAMCommand(mocker):
    return mocker.patch("compiler_admin.services.google.__CallGAMCommand")


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


def test_archive_user_exists(capfd):
    res = user_exists(USER_ARCHIVE)
    captured = capfd.readouterr()

    assert res is True
    assert f"User: {USER_ARCHIVE}" in captured.out
    assert "Google Unique ID:" in captured.out


def test_nonexistent_user_does_not_exist(capfd):
    username = f"nope_does_not_exist@{DOMAIN}"
    res = user_exists(username)
    captured = capfd.readouterr()

    assert res is False
    assert f"User: {username}, Does not exist" in captured.err


def test_nonexistent_not_in_team():
    username = f"nope_does_not_exist@{DOMAIN}"

    assert not user_in_group(username, GROUP_TEAM)


def test_archive_user_not_in_team():
    assert not user_in_group(USER_ARCHIVE, GROUP_TEAM)


def test_archive_user_is_not_partner():
    assert not user_is_partner(USER_ARCHIVE)


def test_archive_user_is_not_staff():
    assert not user_is_staff(USER_ARCHIVE)
