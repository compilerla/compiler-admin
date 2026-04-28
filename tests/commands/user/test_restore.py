import pytest

from compiler_admin import Result
from compiler_admin.commands.user.restore import __name__ as MODULE, restore


@pytest.fixture
def mock_GoogleAccount(mocker):
    return mocker.patch(f"{MODULE}.GoogleAccount").return_value


@pytest.fixture
def mock_GoogleArchive(mocker):
    return mocker.patch(f"{MODULE}.GoogleArchive").return_value


@pytest.fixture
def mock_Path_exists(mocker):
    return mocker.patch(f"{MODULE}.pathlib.Path.exists")


def test_restore__backup_exists(cli_runner, mock_GoogleAccount, mock_GoogleArchive, mock_Path_exists):
    mock_Path_exists.return_value = True

    result = cli_runner.invoke(restore, ["username"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleArchive.restore_email_backup.assert_called_once_with(
        account=mock_GoogleAccount, backup_dir=f"GYB-GMail-Backup-{mock_GoogleAccount}"
    )


def test_restore__backup_does_not_exist(cli_runner, mock_GoogleArchive, mock_Path_exists):
    mock_Path_exists.return_value = False

    result = cli_runner.invoke(restore, ["username"])

    assert result.exit_code != Result.SUCCESS
    assert "Couldn't find a local backup" in result.output
    mock_GoogleArchive.restore_email_backup.assert_not_called
