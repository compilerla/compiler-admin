import pytest

from compiler_admin import RESULT_SUCCESS


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


@pytest.fixture
def mock_commands_create(mock_module_name):
    """Fixture returns a function that patches commands.create in a given module."""
    return mock_module_name("create")


@pytest.fixture
def mock_commands_convert(mock_module_name):
    """Fixture returns a function that patches commands.convert in a given module."""
    return mock_module_name("convert")


@pytest.fixture
def mock_commands_delete(mock_module_name):
    """Fixture returns a function that patches commands.delete in a given module."""
    return mock_module_name("delete")


@pytest.fixture
def mock_commands_info(mock_module_name):
    """Fixture returns a function that patches commands.info in a given module."""
    return mock_module_name("info")


@pytest.fixture
def mock_commands_init(mock_module_name):
    """Fixture returns a function that patches commands.init in a given module."""
    return mock_module_name("init")


@pytest.fixture
def mock_commands_offboard(mock_module_name):
    """Fixture returns a function that patches commands.offboard in a given module."""
    return mock_module_name("offboard")


@pytest.fixture
def mock_commands_reset_password(mock_module_name):
    """Fixture returns a function that patches commands.reset_password in a given module."""
    return mock_module_name("reset_password")


@pytest.fixture
def mock_commands_restore(mock_module_name):
    """Fixture returns a function that patches commands.restore in a given module."""
    return mock_module_name("restore")


@pytest.fixture
def mock_commands_signout(mock_module_name):
    """Fixture returns a function that patches commands.signout in a given module."""
    return mock_module_name("signout")


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
