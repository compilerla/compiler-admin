import pytest

from compiler_admin.commands.init import _clean_config_dir, init, __name__ as MODULE


@pytest.fixture
def mock_rmtree(mocker):
    return mocker.patch(f"{MODULE}.rmtree")


@pytest.fixture
def mock_GAM_CONFIG_PATH(mocker):
    return mocker.patch(f"{MODULE}.GAM_CONFIG_PATH")


@pytest.fixture
def mock_GYB_CONFIG_PATH(mocker):
    return mocker.patch(f"{MODULE}.GYB_CONFIG_PATH")


@pytest.fixture
def mock_clean_config_dir(mocker):
    return mocker.patch(f"{MODULE}._clean_config_dir")


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_subprocess_call(mocker):
    return mocker.patch(f"{MODULE}.subprocess.call")


def test_clean_config_dir(mocker, mock_GAM_CONFIG_PATH, mock_rmtree):
    mock_file = mocker.Mock(is_file=mocker.Mock(return_value=True))
    mock_dir = mocker.Mock(is_file=mocker.Mock(return_value=False), is_dir=mocker.Mock(return_value=True))

    mock_GAM_CONFIG_PATH.glob.return_value = [mock_file, mock_dir]

    _clean_config_dir(mock_GAM_CONFIG_PATH)

    mock_GAM_CONFIG_PATH.mkdir.assert_called_once()
    mock_GAM_CONFIG_PATH.glob.assert_called_once()
    mock_file.is_file.assert_called_once()
    mock_file.unlink.assert_called_once()
    mock_dir.is_file.assert_called_once()
    mock_dir.is_dir.assert_called_once()
    mock_rmtree.assert_called_once()
    assert mock_dir in mock_rmtree.call_args.args


def test_init_default(mock_clean_config_dir, mock_google_CallGAMCommand, mock_subprocess_call):
    init("username")

    assert mock_clean_config_dir.call_count == 0
    assert mock_google_CallGAMCommand.call_count == 0
    assert mock_subprocess_call.call_count == 0


def test_init_gam(mock_GAM_CONFIG_PATH, mock_clean_config_dir, mock_google_CallGAMCommand):
    init("username", gam=True, gyb=False)

    mock_clean_config_dir.assert_called_once()
    assert mock_GAM_CONFIG_PATH in mock_clean_config_dir.call_args.args
    assert mock_google_CallGAMCommand.call_count > 0


def test_init_gyb(mock_GYB_CONFIG_PATH, mock_clean_config_dir, mock_subprocess_call):
    init("username", gam=False, gyb=True)

    mock_clean_config_dir.assert_called_once()
    assert mock_GYB_CONFIG_PATH in mock_clean_config_dir.call_args.args
    assert mock_subprocess_call.call_count > 0
