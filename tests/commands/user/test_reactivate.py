from unittest.mock import call

import pytest

from compiler_admin import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.user.backupcodes import backupcodes
from compiler_admin.commands.user.reactivate import __name__ as MODULE
from compiler_admin.commands.user.reactivate import reactivate
from compiler_admin.commands.user.reset import reset
from compiler_admin.services.google import GROUP_STAFF, GROUP_TEAM, OU_CONTRACTORS, OU_STAFF


@pytest.fixture
def mock_ctx_forward(mocker):
    """Mock click.Context.forward."""
    return mocker.patch("click.Context.forward")


@pytest.fixture
def mock_input_yes(mock_input_yes):
    return mock_input_yes(MODULE)


@pytest.fixture
def mock_input_no(mock_input_no):
    return mock_input_no(MODULE)


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_add_user_to_group(mock_google_add_user_to_group):
    return mock_google_add_user_to_group(MODULE)


@pytest.fixture
def mock_google_move_user_ou(mock_google_move_user_ou):
    return mock_google_move_user_ou(MODULE)


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_user_is_deactivated(mock_module_name):
    return mock_module_name("user_is_deactivated")(MODULE)


def test_reactivate_user_does_not_exist(cli_runner, mock_google_user_exists, mock_google_CallGAMCommand):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code == RESULT_FAILURE
    assert result.exception
    assert "User does not exist: username@compiler.la" in result.output
    mock_google_CallGAMCommand.assert_not_called()


def test_reactivate_user_is_not_deactivated(cli_runner, mock_google_user_exists, mock_google_user_is_deactivated):
    mock_google_user_exists.return_value = True
    mock_google_user_is_deactivated.return_value = False

    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code == RESULT_FAILURE
    assert result.exception
    assert "User is not deactivated, cannot reactivate" in result.output


@pytest.mark.usefixtures("mock_input_no")
def test_reactivate_confirm_no(cli_runner, mock_google_user_exists, mock_google_user_is_deactivated):
    mock_google_user_exists.return_value = True
    mock_google_user_is_deactivated.return_value = True

    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    assert not result.exception
    assert "Aborting reactivation" in result.output


@pytest.mark.usefixtures("mock_input_yes")
def test_reactivate_confirm_yes(
    cli_runner,
    mock_google_user_exists,
    mock_google_user_is_deactivated,
    mock_google_add_user_to_group,
    mock_google_move_user_ou,
    mock_ctx_forward,
):
    mock_google_user_exists.return_value = True
    mock_google_user_is_deactivated.return_value = True

    result = cli_runner.invoke(reactivate, ["username"])

    assert result.exit_code == RESULT_SUCCESS
    assert not result.exception
    mock_google_add_user_to_group.assert_called_once_with("username@compiler.la", GROUP_TEAM)
    mock_google_move_user_ou.assert_called_once_with("username@compiler.la", OU_CONTRACTORS)
    mock_ctx_forward.assert_has_calls([call(reset), call(backupcodes)])


def test_reactivate_force(
    cli_runner,
    mock_google_user_exists,
    mock_google_user_is_deactivated,
    mock_google_add_user_to_group,
    mock_google_move_user_ou,
    mock_ctx_forward,
):
    mock_google_user_exists.return_value = True
    mock_google_user_is_deactivated.return_value = True

    result = cli_runner.invoke(reactivate, ["--force", "username"])

    assert result.exit_code == RESULT_SUCCESS
    assert not result.exception
    mock_google_add_user_to_group.assert_called_once_with("username@compiler.la", GROUP_TEAM)
    mock_google_move_user_ou.assert_called_once_with("username@compiler.la", OU_CONTRACTORS)
    mock_ctx_forward.assert_has_calls([call(reset), call(backupcodes)])


def test_reactivate_staff(
    cli_runner,
    mock_google_user_exists,
    mock_google_user_is_deactivated,
    mock_google_add_user_to_group,
    mock_google_move_user_ou,
    mock_ctx_forward,
):
    mock_google_user_exists.return_value = True
    mock_google_user_is_deactivated.return_value = True

    result = cli_runner.invoke(reactivate, ["--force", "--staff", "username"])

    assert result.exit_code == RESULT_SUCCESS
    assert not result.exception
    mock_google_add_user_to_group.assert_has_calls(
        [call("username@compiler.la", GROUP_TEAM), call("username@compiler.la", GROUP_STAFF)]
    )
    mock_google_move_user_ou.assert_called_once_with("username@compiler.la", OU_STAFF)
    mock_ctx_forward.assert_has_calls([call(reset), call(backupcodes)])


def test_reactivate_recovery_info(
    cli_runner,
    mock_google_user_exists,
    mock_google_user_is_deactivated,
    mock_google_CallGAMCommand,
    mock_ctx_forward,
):
    mock_google_user_exists.return_value = True
    mock_google_user_is_deactivated.return_value = True

    result = cli_runner.invoke(
        reactivate, ["--force", "--recovery-email=foo@bar.com", "--recovery-phone=555-555-5555", "username"]
    )

    assert result.exit_code == RESULT_SUCCESS
    assert not result.exception
    mock_google_CallGAMCommand.assert_has_calls(
        [
            call(("update", "user", "username@compiler.la", "recoveryemail", "foo@bar.com")),
            call(("update", "user", "username@compiler.la", "recoveryphone", "555-555-5555")),
        ]
    )
    mock_ctx_forward.assert_has_calls([call(reset), call(backupcodes)])
