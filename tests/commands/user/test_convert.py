import pytest

from compiler_admin import Result
from compiler_admin.commands.user.convert import __name__ as MODULE, convert


@pytest.fixture
def mock_GoogleAccount(mocker):
    return mocker.patch(f"{MODULE}.GoogleAccount").return_value


@pytest.fixture
def mock_GoogleGroups(mocker):
    return mocker.patch(f"{MODULE}.GoogleGroups").return_value


@pytest.fixture
def mock_GoogleOrgs(mocker):
    return mocker.patch(f"{MODULE}.GoogleOrgs").return_value


@pytest.fixture
def mock_google_OU_CONTRACTORS(mock_GoogleOrgs):
    mock_GoogleOrgs.OU_CONTRACTORS = "/org"
    mock_GoogleOrgs.__getitem__.return_value = "/org"
    return mock_GoogleOrgs


@pytest.fixture
def mock_google_OU_PARTNERS(mock_GoogleOrgs):
    mock_GoogleOrgs.OU_PARTNERS = "/org"
    mock_GoogleOrgs.__getitem__.return_value = "/org"
    return mock_GoogleOrgs


@pytest.fixture
def mock_google_OU_STAFF(mock_GoogleOrgs):
    mock_GoogleOrgs.OU_STAFF = "/org"
    mock_GoogleOrgs.__getitem__.return_value = "/org"
    return mock_GoogleOrgs


@pytest.fixture(autouse=True)
def mock_google_user_exists_true(mock_GoogleAccount, mock_account_exists):
    mock_account_exists(mock_GoogleAccount, True)


@pytest.fixture
def mock_google_user_is_partner_false(mock_GoogleAccount):
    mock_GoogleAccount.is_partner.return_value = False
    return mock_GoogleAccount


@pytest.fixture
def mock_google_user_is_partner_true(mock_GoogleAccount):
    mock_GoogleAccount.is_partner.return_value = True
    return mock_GoogleAccount


@pytest.fixture
def mock_google_user_is_staff_false(mock_GoogleAccount):
    mock_GoogleAccount.is_staff.return_value = False
    return mock_GoogleAccount


@pytest.fixture
def mock_google_user_is_staff_true(mock_GoogleAccount):
    mock_GoogleAccount.is_staff.return_value = True
    return mock_GoogleAccount


def test_convert__user_does_not_exists(cli_runner, mock_account_exists, mock_GoogleAccount, mock_GoogleOrgs):
    mock_account_exists(mock_GoogleAccount, False)

    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code != Result.SUCCESS
    mock_GoogleOrgs.gam_command.assert_not_called()


@pytest.mark.usefixtures("mock_google_user_exists_true")
def test_convert__user_exists__bad_account_type(cli_runner, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "bad_account_type"])

    assert result.exit_code != Result.SUCCESS
    assert mock_GoogleOrgs.call_count == 0


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_false",
    "mock_google_user_is_staff_false",
    "mock_google_OU_CONTRACTORS",
)
def test_convert__contractor(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "contractors"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleOrgs.move_user.assert_called_once()
    mock_GoogleGroups.add_user.assert_not_called()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_true",
    "mock_google_user_is_staff_false",
    "mock_google_OU_CONTRACTORS",
)
def test_convert__contractor__user_is_partner(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "contractors"])

    assert result.exit_code == Result.SUCCESS
    assert mock_GoogleGroups.remove_user.call_count == 2
    mock_GoogleOrgs.move_user.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_false",
    "mock_google_user_is_staff_true",
    "mock_google_OU_CONTRACTORS",
)
def test_convert__contractor__user_is_staff(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "contractors"])

    assert result.exit_code == Result.SUCCESS
    assert mock_GoogleGroups.remove_user.call_count == 1
    mock_GoogleOrgs.move_user.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_false",
    "mock_google_user_is_staff_false",
    "mock_google_OU_STAFF",
)
def test_convert__staff(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleGroups.add_user.assert_called_once()
    mock_GoogleOrgs.move_user.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_true",
    "mock_google_user_is_staff_false",
    "mock_google_OU_STAFF",
)
def test_convert__staff__user_is_partner(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleGroups.remove_user.assert_called_once()
    mock_GoogleGroups.add_user.assert_called_once()
    mock_GoogleOrgs.move_user.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_false",
    "mock_google_user_is_staff_true",
    "mock_google_OU_STAFF",
)
def test_convert__staff__user_is_staff(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code != Result.SUCCESS
    assert "User is already staff" in result.output
    mock_GoogleGroups.add_user.assert_not_called()
    mock_GoogleGroups.remove_user.assert_not_called()
    mock_GoogleOrgs.move_user.assert_not_called()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_false",
    "mock_google_user_is_staff_false",
    "mock_google_OU_PARTNERS",
)
def test_convert__partner(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "partners"])

    assert result.exit_code == Result.SUCCESS
    assert mock_GoogleGroups.add_user.call_count == 2
    mock_GoogleOrgs.move_user.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_true",
    "mock_google_user_is_staff_false",
    "mock_google_OU_PARTNERS",
)
def test_convert__partner__user_is_partner(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "partners"])

    assert result.exit_code != Result.SUCCESS
    assert "User is already partner" in result.output
    mock_GoogleGroups.add_user.assert_not_called()
    mock_GoogleGroups.remove_user.assert_not_called()
    mock_GoogleOrgs.move_user.assert_not_called()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true",
    "mock_google_user_is_partner_false",
    "mock_google_user_is_staff_true",
    "mock_google_OU_PARTNERS",
)
def test_convert__partner__user_is_staff(cli_runner, mock_GoogleGroups, mock_GoogleOrgs):
    result = cli_runner.invoke(convert, ["username", "partners"])

    assert result.exit_code == Result.SUCCESS
    mock_GoogleGroups.add_user.assert_called_once()
    mock_GoogleOrgs.move_user.assert_called_once()
