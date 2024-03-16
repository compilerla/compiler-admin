from argparse import Namespace
import pytest

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.commands.convert import convert, __name__ as MODULE


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


def test_convert_user_username_required():
    args = Namespace()

    with pytest.raises(ValueError, match="username is required"):
        convert(args)


def test_convert_user_account_type_required():
    args = Namespace(username="username")

    with pytest.raises(ValueError, match="account_type is required"):
        convert(args)


def test_convert_user_does_not_exists(mock_google_user_exists, mock_google_move_user_ou):
    mock_google_user_exists.return_value = False

    args = Namespace(username="username", account_type="account_type")
    res = convert(args)

    assert res == RESULT_FAILURE
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures("mock_google_user_exists_true")
def test_convert_user_exists_bad_account_type(mock_google_move_user_ou):
    args = Namespace(username="username", account_type="account_type")
    res = convert(args)

    assert res == RESULT_FAILURE
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures(
    "mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_false"
)
def test_convert_contractor(mock_google_move_user_ou):
    args = Namespace(username="username", account_type="contractor")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_true", "mock_google_user_is_staff_false")
def test_convert_contractor_user_is_partner(mock_google_remove_user_from_group, mock_google_move_user_ou):
    args = Namespace(username="username", account_type="contractor")
    res = convert(args)

    assert res == RESULT_SUCCESS
    assert mock_google_remove_user_from_group.call_count == 2
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_true")
def test_convert_contractor_user_is_staff(mock_google_remove_user_from_group, mock_google_move_user_ou):
    args = Namespace(username="username", account_type="contractor")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_google_remove_user_from_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures(
    "mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_false"
)
def test_convert_staff(mock_google_add_user_to_group, mock_google_move_user_ou):
    args = Namespace(username="username", account_type="staff")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_google_add_user_to_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_true", "mock_google_user_is_staff_false")
def test_convert_staff_user_is_partner(
    mock_google_add_user_to_group, mock_google_remove_user_from_group, mock_google_move_user_ou
):
    args = Namespace(username="username", account_type="staff")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_google_remove_user_from_group.assert_called_once()
    mock_google_add_user_to_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_true")
def test_convert_staff_user_is_staff(mock_google_add_user_to_group, mock_google_move_user_ou):
    args = Namespace(username="username", account_type="staff")
    res = convert(args)

    assert res == RESULT_FAILURE
    assert mock_google_add_user_to_group.call_count == 0
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures(
    "mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_false"
)
def test_convert_partner(mock_google_add_user_to_group, mock_google_move_user_ou):
    args = Namespace(username="username", account_type="partner")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_google_add_user_to_group.call_count == 2
    mock_google_move_user_ou.assert_called_once()


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_true", "mock_google_user_is_staff_false")
def test_convert_partner_user_is_partner(mock_google_add_user_to_group, mock_google_move_user_ou):
    args = Namespace(username="username", account_type="partner")
    res = convert(args)

    assert res == RESULT_FAILURE
    assert mock_google_add_user_to_group.call_count == 0
    assert mock_google_move_user_ou.call_count == 0


@pytest.mark.usefixtures("mock_google_user_exists_true", "mock_google_user_is_partner_false", "mock_google_user_is_staff_true")
def test_convert_partner_user_is_staff(mock_google_add_user_to_group, mock_google_move_user_ou):
    args = Namespace(username="username", account_type="partner")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_google_add_user_to_group.assert_called_once()
    mock_google_move_user_ou.assert_called_once()
