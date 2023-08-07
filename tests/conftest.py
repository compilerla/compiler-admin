import pytest


@pytest.fixture
def mock_commands_create(mocker):
    """Fixture returns a function that patches commands.create in a given module."""

    def _mock_commands_create(module, **kwargs):
        return mocker.patch(f"{module}.create", **kwargs)

    return _mock_commands_create


@pytest.fixture
def mock_commands_convert(mocker):
    """Fixture returns a function that patches commands.convert in a given module."""

    def _mock_commands_convert(module, **kwargs):
        return mocker.patch(f"{module}.convert", **kwargs)

    return _mock_commands_convert


@pytest.fixture
def mock_commands_delete(mocker):
    """Fixture returns a function that patches commands.delete in a given module."""

    def _mock_commands_delete(module, **kwargs):
        return mocker.patch(f"{module}.delete", **kwargs)

    return _mock_commands_delete


@pytest.fixture
def mock_commands_info(mocker):
    """Fixture returns a function that patches commands.info in a given module."""

    def _mock_commands_info(module, **kwargs):
        return mocker.patch(f"{module}.info", **kwargs)

    return _mock_commands_info


@pytest.fixture
def mock_commands_init(mocker):
    """Fixture returns a function that patches commands.init in a given module."""

    def _mock_commands_init(module, **kwargs):
        return mocker.patch(f"{module}.init", **kwargs)

    return _mock_commands_init


@pytest.fixture
def mock_commands_offboard(mocker):
    """Fixture returns a function that patches commands.offboard in a given module."""

    def _mock_commands_offboard(module, **kwargs):
        return mocker.patch(f"{module}.offboard", **kwargs)

    return _mock_commands_offboard


@pytest.fixture
def mock_commands_restore(mocker):
    """Fixture returns a function that patches commands.restore in a given module."""

    def _mock_commands_restore(module, **kwargs):
        return mocker.patch(f"{module}.restore", **kwargs)

    return _mock_commands_restore


@pytest.fixture
def mock_commands_signout(mocker):
    """Fixture returns a function that patches commands.signout in a given module."""

    def _mock_commands_signout(module, **kwargs):
        return mocker.patch(f"{module}.signout", **kwargs)

    return _mock_commands_signout


@pytest.fixture
def mock_google_CallGAMCommand(mocker):
    """Fixture returns a function that patches the CallGAMCommand function from a given module."""

    def _mock_google_CallGAMCommand(module, **kwargs):
        return mocker.patch(f"{module}.CallGAMCommand", **kwargs)

    return _mock_google_CallGAMCommand


@pytest.fixture
def mock_google_CallGYBCommand(mocker):
    """Fixture returns a function that patches the CallGYBCommand function from a given module."""

    def _mock_google_CallGYBCommand(module, **kwargs):
        return mocker.patch(f"{module}.CallGYBCommand", **kwargs)

    return _mock_google_CallGYBCommand


@pytest.fixture
def mock_google_add_user_to_group(mocker):
    """Fixture returns a function that patches the add_user_to_group function from a given module."""

    def _mock_google_add_user_to_group(module, **kwargs):
        return mocker.patch(f"{module}.add_user_to_group", **kwargs)

    return _mock_google_add_user_to_group


@pytest.fixture
def mock_google_move_user_ou(mocker):
    """Fixture returns a function that patches the move_user_ou function from a given module."""

    def _mock_google_move_user_ou(module, **kwargs):
        return mocker.patch(f"{module}.move_user_ou", **kwargs)

    return _mock_google_move_user_ou


@pytest.fixture
def mock_google_remove_user_from_group(mocker):
    """Fixture returns a function that patches the remove_user_from_group function from a given module."""

    def _mock_google_remove_user_from_group(module, **kwargs):
        return mocker.patch(f"{module}.remove_user_from_group", **kwargs)

    return _mock_google_remove_user_from_group


@pytest.fixture
def mock_google_user_exists(mocker):
    """Fixture returns a function that patches the user_exists function from a given module."""

    def _mock_google_user_exists(module, **kwargs):
        return mocker.patch(f"{module}.user_exists", **kwargs)

    return _mock_google_user_exists


@pytest.fixture
def mock_google_user_in_group(mocker):
    """Fixture returns a function that patches the user_in_group function from a given module."""

    def _mock_google_user_in_group(module, **kwargs):
        return mocker.patch(f"{module}.user_in_group", **kwargs)

    return _mock_google_user_in_group


@pytest.fixture
def mock_google_user_is_partner(mocker):
    """Fixture returns a function that patches the user_is_partner function from a given module."""

    def _mock_google_user_is_partner(module, **kwargs):
        return mocker.patch(f"{module}.user_is_partner", **kwargs)

    return _mock_google_user_is_partner


@pytest.fixture
def mock_google_user_is_staff(mocker):
    """Fixture returns a function that patches the user_is_staff function from a given module."""

    def _mock_google_user_is_staff(module, **kwargs):
        return mocker.patch(f"{module}.user_is_staff", **kwargs)

    return _mock_google_user_is_staff


@pytest.fixture
def mock_NamedTemporaryFile(mocker):
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
