import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.info import info, __name__ as MODULE
from compiler_admin.services.google import DOMAIN


@pytest.fixture
def mock_google_CallGAMCommand(mock_google_CallGAMCommand):
    return mock_google_CallGAMCommand(MODULE)


@pytest.fixture
def mock_google_CallGYBCommand(mock_google_CallGYBCommand):
    return mock_google_CallGYBCommand(MODULE)


def test_info(mock_google_CallGAMCommand, mock_google_CallGYBCommand):
    info()

    assert mock_google_CallGAMCommand.call_count > 0
    mock_google_CallGYBCommand.assert_called_once()


@pytest.mark.e2e
def test_info_e2e(capfd):
    res = info()
    captured = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "compiler-admin:" in captured.out
    assert "GAMADV-XTD3" in captured.out
    assert f"Primary Domain: {DOMAIN}" in captured.out
    assert "Got Your Back" in captured.out
    assert "WARNING: Config File:" not in captured.err
