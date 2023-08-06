import pytest


@pytest.fixture
def mock_CallGAMCommand(mocker):
    """Fixture returns a function that patches the CallGAMCommand function from a given module."""

    def _mock_CallGAMCommand(module, **kwargs):
        return mocker.patch(f"{module}.CallGAMCommand", **kwargs)

    return _mock_CallGAMCommand


@pytest.fixture
def mock_user_exists(mocker):
    """Fixture returns a function that patches the user_exists function from a given module."""

    def _mock_user_exists(module, **kwargs):
        return mocker.patch(f"{module}.user_exists", **kwargs)

    return _mock_user_exists


@pytest.fixture
def mock_add_user_to_group(mocker):
    """Fixture returns a function that patches the add_user_to_group function from a given module."""

    def _mock_add_user_to_group(module, **kwargs):
        return mocker.patch(f"{module}.add_user_to_group", **kwargs)

    return _mock_add_user_to_group


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


@pytest.fixture
def mock_signout(mocker):
    """Fixture returns a function that patches commands.signout in a given module."""

    def _mock_signout(module, **kwargs):
        return mocker.patch(f"{module}.signout", **kwargs)

    return _mock_signout


@pytest.fixture
def mock_delete(mocker):
    """Fixture returns a function that patches commands.delete in a given module."""

    def _mock_delete(module, **kwargs):
        return mocker.patch(f"{module}.delete", **kwargs)

    return _mock_delete
