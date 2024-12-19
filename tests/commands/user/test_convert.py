import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.user.convert import convert, __name__ as MODULE


@pytest.fixture
def mock_commands_alumni(mock_commands_alumni):
    return mock_commands_alumni(MODULE)


@pytest.fixture
def mock_google_user_exists(mock_google_user_exists):
    return mock_google_user_exists(MODULE)


@pytest.fixture
def mock_google_user_exists_true(mock_google_user_exists):
    mock_google_user_exists.return_value = True
    return mock_google_user_exists


@pytest.fixture
def mock_google_add_user_to_group(mock_google_add_user_to_group):
    return mock_google_add_user_to_group(MODULE)


@pytest.fixture
def mock_google_move_user_ou(mock_google_move_user_ou):
    return mock_google_move_user_ou(MODULE)


@pytest.fixture
def mock_google_remove_user_from_group(mock_google_remove_user_from_group):
    return mock_google_remove_user_from_group(MODULE)


@pytest.fixture
def mock_google_user_is_partner(mock_google_user_is_partner):
    return mock_google_user_is_partner(MODULE)


@pytest.fixture
def mock_google_user_is_partner_true(mock_google_user_is_partner):
    mock_google_user_is_partner.return_value = True
    return mock_google_user_is_partner


@pytest.fixture
def mock_google_user_is_partner_false(mock_google_user_is_partner):
    mock_google_user_is_partner.return_value = False
    return mock_google_user_is_partner


@pytest.fixture
def mock_google_user_is_staff(mock_google_user_is_staff):
    return mock_google_user_is_staff(MODULE)


@pytest.fixture
def mock_google_user_is_staff_true(mock_google_user_is_staff):
    mock_google_user_is_staff.return_value = True
    return mock_google_user_is_staff


@pytest.fixture
def mock_google_user_is_staff_false(mock_google_user_is_staff):
    mock_google_user_is_staff.return_value = False
    return mock_google_user_is_staff


def test_convert_user_does_not_exists(cli_runner, mock_google_user_exists, mock_google_move_user_ou):
    mock_google_user_exists.return_value = False

    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code != RESULT_SUCCESS
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures("mock_google_user_exists_true")
def test_convert_user_exists_bad_account_type(cli_runner, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "bad_account_type"])

    assert result.exit_code != RESULT_SUCCESS
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures("mock_google_user_exists_true")
def test_convert_alumni(cli_runner, mock_commands_alumni, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "alumni"])

    assert result.exit_code == RESULT_SUCCESS
    mock_commands_alumni.callback.assert_called_once()
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_false"
)
def test_convert_contractor(cli_runner, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "contractor"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_true", "mock_google_user_is_staff_false")
def test_convert_contractor_user_is_partner(cli_runner, mock_google_remove_user_from_group, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "contractor"])

    assert result.exit_code == RESULT_SUCCESS
    assert mock_google_remove_user_from_group.call_count == 2
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_true")
def test_convert_contractor_user_is_staff(cli_runner, mock_google_remove_user_from_group, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "contractor"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_remove_user_from_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_false"
)
def test_convert_staff(cli_runner, mock_google_add_user_to_group, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_add_user_to_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_true", "mock_google_user_is_staff_false")
def test_convert_staff_user_is_partner(
    cli_runner, mock_google_add_user_to_group, mock_google_remove_user_from_group, mock_google_move_user_ou
):
    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_remove_user_from_group.assert_called_once()
    mock_google_add_user_to_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_true")
def test_convert_staff_user_is_staff(cli_runner, mock_google_add_user_to_group, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "staff"])

    assert result.exit_code != RESULT_SUCCESS
    assert mock_google_add_user_to_group.call_count == 0
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures(
    "mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_false"
)
def test_convert_partner(cli_runner, mock_google_add_user_to_group, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "partner"])

    assert result.exit_code == RESULT_SUCCESS
    assert mock_google_add_user_to_group.call_count == 2
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_true", "mock_google_user_is_staff_false")
def test_convert_partner_user_is_partner(cli_runner, mock_google_add_user_to_group, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "partner"])

    assert result != RESULT_SUCCESS
    assert mock_google_add_user_to_group.call_count == 0
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_true")
def test_convert_partner_user_is_staff(cli_runner, mock_google_add_user_to_group, mock_google_move_user_ou):
    result = cli_runner.invoke(convert, ["username", "partner"])

    assert result.exit_code == RESULT_SUCCESS
    mock_google_add_user_to_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()
