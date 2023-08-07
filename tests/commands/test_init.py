import pytest

from compiler_admin.commands.init import init, __name__ as MODULE


@pytest.fixture
def mock_CONFIG_PATH(mocker):
    return mocker.patch(f"{MODULE}.CONFIG_PATH")


@pytest.fixture
def mock_clean_config_dir(mocker):
    return mocker.patch(f"{MODULE}._clean_config_dir")


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_subprocess_call(mocker):
    return mocker.patch(f"{MODULE}.subprocess.call")


def test_init_config_path_exists(mock_CONFIG_PATH, mock_clean_config_dir, mock_google_CallGAMCommand, mock_subprocess_call):
    mock_CONFIG_PATH.exists.return_value = True

    init("username")

    mock_clean_config_dir.assert_called_once()
    assert mock_google_CallGAMCommand.call_count > 0
    assert mock_subprocess_call.call_count > 0


def test_init_config_path_does_not_exist(
    mock_CONFIG_PATH, mock_clean_config_dir, mock_google_CallGAMCommand, mock_subprocess_call
):
    mock_CONFIG_PATH.exists.return_value = False

    init("username")

    assert mock_clean_config_dir.call_count == 0
    assert mock_google_CallGAMCommand.call_count > 0
    assert mock_subprocess_call.call_count > 0
