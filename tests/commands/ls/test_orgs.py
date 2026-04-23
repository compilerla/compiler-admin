import pytest

from compiler_admin import Result
from compiler_admin.commands.ls.orgs import __name__ as MODULE, orgs


@pytest.fixture
def mock_GoogleOrgs(mocker):
    return mocker.patch(f"{MODULE}.GoogleOrgs").return_value


def test_orgs(cli_runner, mock_GoogleOrgs):
    args = []
    result = cli_runner.invoke(orgs, args)

    assert result.exit_code == Result.SUCCESS

    mock_GoogleOrgs.get.assert_called_once_with()
