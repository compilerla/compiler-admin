import pytest


@pytest.fixture
def mock_CallGAMCommand(mocker):
    """Fixture returns a function that patches the CallGAMCommand function from a given module."""

    def _mock_CallGAMCommand(module, **kwargs):
        return mocker.patch(f"{module}.CallGAMCommand", **kwargs)

    return _mock_CallGAMCommand


@pytest.fixture
def mock_CallGAMCommand_RedirectOutErr(mocker):
    """Fixture returns a function that patches the CallGAMCommand_RedirectOutErr function from a given module."""

    def _mock_CallGAMCommand(module, **kwargs):
        return mocker.patch(f"{module}.CallGAMCommand_RedirectOutErr", **kwargs)

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
    """Fixture returns a function that patches NamedTemporaryFile in a given module."""

    def _mock_NamedTemporaryFile(module, **kwargs):
        return mocker.patch(f"{module}.NamedTemporaryFile", **kwargs)

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
