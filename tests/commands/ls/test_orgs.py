import pytest

from compiler_admin import Result
from compiler_admin.commands.ls.orgs import __name__ as MODULE, orgs


@pytest.fixture
def mock_google_get_org_units(mocker):
    return mocker.patch(f"{MODULE}.get_org_units")


def test_orgs(cli_runner, mock_google_get_org_units):
    args = []
    result = cli_runner.invoke(orgs, args)

    assert result.exit_code == Result.SUCCESS
    mock_google_get_org_units.assert_called_once_with()
