import click
import pytest
from click.testing import CliRunner
from pytest_socket import disable_socket

from compiler_admin import Result
from compiler_admin.services.google import GoogleAccount, GoogleService


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def mock_module_name(mocker):
    """Fixture returns a function taking a name, that returns a function taking a module,
    patching the given name in the given module.

    By default, the patched object is given a return_value = ResultCodes.SUCCESS.
    """

    def _mock_module_name(name):
        def __mock_module_name(module):
            patched = mocker.patch(f"{module}.{name}")
            patched.return_value = Result.SUCCESS
            return patched

        return __mock_module_name

    return _mock_module_name


@pytest.fixture
def mock_input(mock_module_name):
    """Fixture returns a function that patches the built-in input in a given module."""
    return mock_module_name("input")


@pytest.fixture
def mock_input_yes(mock_input):
    """Fixture returns a function that patches the input return value to Yes in a give module."""

    def _mock_input_yes(module):
        fix = mock_input(module)
        fix.return_value = "y"
        return fix

    return _mock_input_yes


@pytest.fixture
def mock_input_no(mock_input):
    """Fixture returns a function that patches the input return value to No in a give module."""

    def _mock_input_no(module):
        fix = mock_input(module)
        fix.return_value = "n"
        return fix

    return _mock_input_no


@click.command
def dummy_command(**kwargs):
    return Result.SUCCESS


@pytest.fixture
def mock_command(mocker):
    def _mock_command(command):
        def __mock_command(module):
            return mocker.patch(f"{module}.{command}", new=mocker.MagicMock(spec=dummy_command))

        return __mock_command

    return _mock_command


@pytest.fixture
def mock_commands_backupcodes(mock_command):
    """Fixture returns a function that patches the backupcodes function in a given module."""
    return mock_command("backupcodes")


@pytest.fixture
def mock_commands_deactivate(mock_command):
    """Fixture returns a function that patches the deactivate function in a given module."""
    return mock_command("deactivate")


@pytest.fixture
def mock_commands_delete(mock_command):
    """Fixture returns a function that patches the delete command function in a given module."""
    return mock_command("delete")


@pytest.fixture
def mock_commands_reset(mock_command):
    """Fixture returns a function that patches the reset command function in a given module."""
    return mock_command("reset")


@pytest.fixture
def mock_commands_signout(mock_command):
    """Fixture returns a function that patches the signout command function in a given module."""
    return mock_command("signout")


@pytest.fixture
def mock_google_CallGAMCommand(mock_module_name):
    """Fixture returns a function that patches the CallGAMCommand function from a given module."""
    return mock_module_name("CallGAMCommand")


@pytest.fixture
def mock_google_CallGYBCommand(mock_module_name):
    """Fixture returns a function that patches the CallGYBCommand function from a given module."""
    return mock_module_name("CallGYBCommand")


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
def mock_account_exists(mocker):
    """Returns a function that mocks the exists method on a GoogleAccounts instance."""

    def _mock_account_exists(account: GoogleAccount, exists: bool = True) -> bool:
        return mocker.patch.object(account, "exists", return_value=exists)

    return _mock_account_exists


@pytest.fixture
def mock_gam_gyb(mocker):
    """Returns a function that mocks the GAM and GYB commands on a GoogleService."""

    def _mock_gam_gyb(service: GoogleService) -> GoogleService:
        mocker.patch.object(service, "gam_command")
        mocker.patch.object(service, "gam_command_output")
        mocker.patch.object(service, "gyb_command")
        return service

    return _mock_gam_gyb


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
