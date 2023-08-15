import subprocess

import pytest

from compiler_admin import __version__ as version
import compiler_admin.main
from compiler_admin.main import main, __name__ as MODULE
from compiler_admin.services.google import DOMAIN


@pytest.fixture
def mock_commands_create(mock_commands_create):
    return mock_commands_create(MODULE)


@pytest.fixture
def mock_commands_convert(mock_commands_convert):
    return mock_commands_convert(MODULE)


@pytest.fixture
def mock_commands_delete(mock_commands_delete):
    return mock_commands_delete(MODULE)


@pytest.fixture
def mock_commands_info(mock_commands_info):
    return mock_commands_info(MODULE)


@pytest.fixture
def mock_commands_init(mock_commands_init):
    return mock_commands_init(MODULE)


@pytest.fixture
def mock_commands_offboard(mock_commands_offboard):
    return mock_commands_offboard(MODULE)


@pytest.fixture
def mock_commands_restore(mock_commands_restore):
    return mock_commands_restore(MODULE)


@pytest.fixture
def mock_commands_signout(mock_commands_signout):
    return mock_commands_signout(MODULE)


def test_main_create(mock_commands_create):
    main(argv=["create", "username"])

    mock_commands_create.assert_called_once()
    call_args = mock_commands_create.call_args.args
    assert "username" in call_args


def test_main_create_no_username(mock_commands_create):
    with pytest.raises(SystemExit):
        main(argv=["create"])
        assert mock_commands_create.call_count == 0


def test_main_convert(mock_commands_convert):
    main(argv=["convert", "username", "contractor"])

    mock_commands_convert.assert_called_once()
    call_args = mock_commands_convert.call_args.args
    assert call_args == ("username", "contractor")


def test_main_convert_no_username(mock_commands_convert):
    with pytest.raises(SystemExit):
        main(argv=["convert"])
        assert mock_commands_convert.call_count == 0


def test_main_convert_bad_account_type(mock_commands_convert):
    with pytest.raises(SystemExit):
        main(argv=["convert", "username", "account_type"])
        assert mock_commands_convert.call_count == 0


def test_main_delete(mock_commands_delete):
    main(argv=["delete", "username"])

    mock_commands_delete.assert_called_once()
    call_args = mock_commands_delete.call_args.args
    assert "username" in call_args


def test_main_delete_no_username(mock_commands_delete):
    with pytest.raises(SystemExit):
        main(argv=["delete"])
        assert mock_commands_delete.call_count == 0


def test_main_info(mock_commands_info):
    main(argv=["info"])

    mock_commands_info.assert_called_once()


def test_main_info_default(mock_commands_info):
    main(argv=[])

    mock_commands_info.assert_called_once()


def test_main_init_default(mock_commands_init):
    main(argv=["init", "username"])

    mock_commands_init.assert_called_once()
    assert mock_commands_init.call_args.args == ("username",)
    assert mock_commands_init.call_args.kwargs == {"gam": False, "gyb": False}


def test_main_init_gam(mock_commands_init):
    main(argv=["init", "username", "--gam"])

    mock_commands_init.assert_called_once()
    assert mock_commands_init.call_args.args == ("username",)
    assert mock_commands_init.call_args.kwargs == {"gam": True, "gyb": False}


def test_main_init_gyb(mock_commands_init):
    main(argv=["init", "username", "--gyb"])

    mock_commands_init.assert_called_once()
    assert mock_commands_init.call_args.args == ("username",)
    assert mock_commands_init.call_args.kwargs == {"gam": False, "gyb": True}


def test_main_init_no_username(mock_commands_init):
    with pytest.raises(SystemExit):
        main(argv=["init"])
        assert mock_commands_init.call_count == 0


def test_main_offboard(mock_commands_offboard):
    main(argv=["offboard", "username"])

    mock_commands_offboard.assert_called_once()
    call_args = mock_commands_offboard.call_args.args
    assert "username" in call_args


def test_main_offboard_with_alias(mock_commands_offboard):
    main(argv=["offboard", "username", "--alias", "anotheruser"])

    mock_commands_offboard.assert_called_once()
    assert mock_commands_offboard.call_args.args == ("username", "anotheruser")


def test_main_offboard_no_username(mock_commands_offboard):
    with pytest.raises(SystemExit):
        main(argv=["offboard"])
        assert mock_commands_offboard.call_count == 0


def test_main_restore(mock_commands_restore):
    main(argv=["restore", "username"])

    mock_commands_restore.assert_called_once()
    call_args = mock_commands_restore.call_args.args
    assert "username" in call_args


def test_main_restore_no_username(mock_commands_restore):
    with pytest.raises(SystemExit):
        main(argv=["restore"])
        assert mock_commands_restore.call_count == 0


def test_main_signout(mock_commands_signout):
    main(argv=["signout", "username"])

    mock_commands_signout.assert_called_once()
    call_args = mock_commands_signout.call_args.args
    assert "username" in call_args


def test_main_signout_no_username(mock_commands_signout):
    with pytest.raises(SystemExit):
        main(argv=["signout"])
        assert mock_commands_signout.call_count == 0


@pytest.mark.e2e
def test_main_e2e(mocker):
    spy_info = mocker.spy(compiler_admin.main, "info")
    res = main(argv=[])

    assert res == 0
    spy_info.assert_called_once()


@pytest.mark.e2e
def test_run_compiler_admin(capfd):
    # call CLI command as a subprocess
    res = subprocess.call(["compiler-admin"])
    captured = capfd.readouterr()

    assert res == 0
    assert f"compiler-admin: {version}" in captured.out
    assert "GAMADV-XTD3" in captured.out
    assert f"Primary Domain: {DOMAIN}" in captured.out
    assert "WARNING: Config File:" not in captured.err
