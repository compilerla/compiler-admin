import click
from click.testing import CliRunner

import pytest
from pytest_socket import disable_socket

from compiler_admin import RESULT_SUCCESS


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def mock_module_name(mocker):
    """Fixture returns a function taking a name, that returns a function taking a module,
    patching the given name in the given module.

    By default, the patched object is given a return_value = RESULT_SUCCESS.
    """

    def _mock_module_name(name):
        def __mock_module_name(module):
            patched = mocker.patch(f"{module}.{name}")
            patched.return_value = RESULT_SUCCESS
            return patched

        return __mock_module_name

    return _mock_module_name


@pytest.fixture
def mock_input(mock_module_name):
    """Fixture returns a function that patches the built-in input in a given module."""
    return mock_module_name("input")


@click.command
def dummy_command(**kwargs):
    return RESULT_SUCCESS


@pytest.fixture
def mock_command(mocker):
    def _mock_command(command):
        def __mock_command(module):
            return mocker.patch(f"{module}.{command}", new=mocker.MagicMock(spec=dummy_command))

        return __mock_command

    return _mock_command


@pytest.fixture
def mock_commands_alumni(mock_command):
    """Fixture returns a function that patches the alumni function in a given module."""
    return mock_command("alumni")


@pytest.fixture
def mock_commands_create(mock_command):
    """Fixture returns a function that patches the create function in a given module."""
    return mock_command("create")


@pytest.fixture
def mock_commands_convert(mock_command):
    """Fixture returns a function that patches the convert command function in a given module."""
    return mock_command("convert")


@pytest.fixture
def mock_commands_delete(mock_command):
    """Fixture returns a function that patches the delete command function in a given module."""
    return mock_command("delete")


@pytest.fixture
def mock_commands_info(mock_command):
    """Fixture returns a function that patches the info command function in a given module."""
    return mock_command("info")


@pytest.fixture
def mock_commands_init(mock_command):
    """Fixture returns a function that patches the init command function in a given module."""
    return mock_command("init")


@pytest.fixture
def mock_commands_offboard(mock_command):
    """Fixture returns a function that patches the offboard command function in a given module."""
    return mock_command("offboard")


@pytest.fixture
def mock_commands_reset(mock_command):
    """Fixture returns a function that patches the reset command function in a given module."""
    return mock_command("reset")


@pytest.fixture
def mock_commands_restore(mock_command):
    """Fixture returns a function that patches the restore command function in a given module."""
    return mock_command("restore")


@pytest.fixture
def mock_commands_signout(mock_command):
    """Fixture returns a function that patches the signout command function in a given module."""
    return mock_command("signout")


@pytest.fixture
def mock_commands_time(mock_command):
    """Fixture returns a function that patches the time command function in a given module."""
    return mock_command("time")


@pytest.fixture
def mock_commands_user(mock_command):
    """Fixture returns a function that patches the user command function in a given module."""
    return mock_command("user")


@pytest.fixture
def mock_google_CallGAMCommand(mock_module_name):
    """Fixture returns a function that patches the CallGAMCommand function from a given module."""
    return mock_module_name("CallGAMCommand")


@pytest.fixture
def mock_google_CallGYBCommand(mock_module_name):
    """Fixture returns a function that patches the CallGYBCommand function from a given module."""
    return mock_module_name("CallGYBCommand")


@pytest.fixture
def mock_google_add_user_to_group(mock_module_name):
    """Fixture returns a function that patches the add_user_to_group function from a given module."""
    return mock_module_name("add_user_to_group")


@pytest.fixture
def mock_google_move_user_ou(mock_module_name):
    """Fixture returns a function that patches the move_user_ou function from a given module."""
    return mock_module_name("move_user_ou")


@pytest.fixture
def mock_google_remove_user_from_group(mock_module_name):
    """Fixture returns a function that patches the remove_user_from_group function from a given module."""
    return mock_module_name("remove_user_from_group")


@pytest.fixture
def mock_google_user_exists(mock_module_name):
    """Fixture returns a function that patches the user_exists function from a given module."""
    return mock_module_name("user_exists")


@pytest.fixture
def mock_google_user_info(mock_module_name):
    """Fixture returns a function that patches the user_info function from a given module."""
    return mock_module_name("user_info")


@pytest.fixture
def mock_google_user_in_group(mock_module_name):
    """Fixture returns a function that patches the user_in_group function from a given module."""
    return mock_module_name("user_in_group")


@pytest.fixture
def mock_google_user_is_partner(mock_module_name):
    """Fixture returns a function that patches the user_is_partner function from a given module."""
    return mock_module_name("user_is_partner")


@pytest.fixture
def mock_google_user_is_staff(mock_module_name):
    """Fixture returns a function that patches the user_is_staff function from a given module."""
    return mock_module_name("user_is_staff")


@pytest.fixture
def mock_NamedTemporaryFile_with_readlines(mocker):
    """Fixture returns a function that patches NamedTemporaryFile in a given module.

    Optionally provide a value for GAM stdout.readlines().
    """

    def _mock_NamedTemporaryFile(module, readlines=[""], **kwargs):
        patched = mocker.patch(f"{module}.NamedTemporaryFile", **kwargs)
        # mock the enter/exit methods to fake a context manager
        # supporting mocking of the "with" context for a NamedTemporaryFile
        # idea from https://stackoverflow.com/a/28852060
        mock_stdout = mocker.Mock()
        mock_stdout.__enter__ = mocker.Mock(return_value=mocker.Mock(readlines=mocker.Mock(return_value=readlines)))
        mock_stdout.__exit__ = mocker.Mock()
        patched.return_value = mock_stdout
        return patched

    return _mock_NamedTemporaryFile


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def harvest_file():
    return "notebooks/data/harvest-sample.csv"


@pytest.fixture
def justworks_file():
    return "notebooks/data/justworks-sample.csv"


@pytest.fixture
def toggl_file():
    return "notebooks/data/toggl-sample.csv"
