from argparse import Namespace
from datetime import datetime
import subprocess
import sys

import pytest

import compiler_admin.main
from compiler_admin.main import main, prior_month_start, prior_month_end, TZINFO, __name__ as MODULE
from compiler_admin.services.google import DOMAIN


@pytest.fixture
def mock_local_now(mocker):
    dt = datetime(2024, 9, 25, tzinfo=TZINFO)
    mocker.patch(f"{MODULE}.local_now", return_value=dt)
    return dt


@pytest.fixture
def mock_start(mock_local_now):
    return datetime(2024, 8, 1, tzinfo=TZINFO)


@pytest.fixture
def mock_end(mock_local_now):
    return datetime(2024, 8, 31, tzinfo=TZINFO)


@pytest.fixture
def mock_commands_info(mock_commands_info):
    return mock_commands_info(MODULE)


@pytest.fixture
def mock_commands_init(mock_commands_init):
    return mock_commands_init(MODULE)


@pytest.fixture
def mock_commands_time(mock_commands_time):
    return mock_commands_time(MODULE)


@pytest.fixture
def mock_commands_user(mock_commands_user):
    return mock_commands_user(MODULE)


def test_prior_month_start(mock_start):
    start = prior_month_start()

    assert start == mock_start


def test_prior_month_end(mock_end):
    end = prior_month_end()

    assert end == mock_end


def test_main_info(mock_commands_info):
    main(argv=["info"])

    mock_commands_info.assert_called_once()


def test_main_info_default(mock_commands_info):
    main(argv=[])

    mock_commands_info.assert_called_once()


def test_main_init_default(mock_commands_init):
    main(argv=["init", "username"])

    mock_commands_init.assert_called_once()
    call_args = mock_commands_init.call_args.args
    assert Namespace(func=mock_commands_init, command="init", username="username", gam=False, gyb=False) in call_args


def test_main_init_gam(mock_commands_init):
    main(argv=["init", "username", "--gam"])

    mock_commands_init.assert_called_once()
    call_args = mock_commands_init.call_args.args
    assert Namespace(func=mock_commands_init, command="init", username="username", gam=True, gyb=False) in call_args


def test_main_init_gyb(mock_commands_init):
    main(argv=["init", "username", "--gyb"])

    mock_commands_init.assert_called_once()
    call_args = mock_commands_init.call_args.args
    assert Namespace(func=mock_commands_init, command="init", username="username", gam=False, gyb=True) in call_args


def test_main_init_no_username(mock_commands_init):
    with pytest.raises(SystemExit):
        main(argv=["init"])
        assert mock_commands_init.call_count == 0


def test_main_time_convert_default(mock_commands_time):
    main(argv=["time", "convert"])

    mock_commands_time.assert_called_once()
    call_args = mock_commands_time.call_args.args
    assert (
        Namespace(
            func=mock_commands_time, command="time", subcommand="convert", client=None, input=sys.stdin, output=sys.stdout
        )
        in call_args
    )


@pytest.mark.usefixtures("mock_local_now")
def test_main_time_download_default(mock_commands_time, mock_start, mock_end):
    main(argv=["time", "download"])

    mock_commands_time.assert_called_once()
    call_args = mock_commands_time.call_args.args
    assert (
        Namespace(
            func=mock_commands_time,
            command="time",
            subcommand="download",
            start=mock_start,
            end=mock_end,
            output=sys.stdout,
            client_ids=None,
            project_ids=None,
            task_ids=None,
            user_ids=None,
        )
        in call_args
    )


def test_main_time_download_args(mock_commands_time):
    main(
        argv=[
            "time",
            "download",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-31",
            "--output",
            "file.csv",
            "--client",
            "1",
            "--client",
            "2",
            "--client",
            "3",
            "--project",
            "1",
            "--project",
            "2",
            "--project",
            "3",
            "--task",
            "1",
            "--task",
            "2",
            "--task",
            "3",
            "--user",
            "1",
            "--user",
            "2",
            "--user",
            "3",
        ]
    )

    expected_start = TZINFO.localize(datetime(2024, 1, 1))
    expected_end = TZINFO.localize(datetime(2024, 1, 31))
    ids = [1, 2, 3]

    mock_commands_time.assert_called_once()
    call_args = mock_commands_time.call_args.args
    assert (
        Namespace(
            func=mock_commands_time,
            command="time",
            subcommand="download",
            start=expected_start,
            end=expected_end,
            output="file.csv",
            client_ids=ids,
            project_ids=ids,
            task_ids=ids,
            user_ids=ids,
        )
        in call_args
    )


def test_main_time_convert_client(mock_commands_time):
    main(argv=["time", "convert", "--client", "client123"])

    mock_commands_time.assert_called_once()
    call_args = mock_commands_time.call_args.args
    assert (
        Namespace(
            func=mock_commands_time,
            command="time",
            subcommand="convert",
            client="client123",
            input=sys.stdin,
            output=sys.stdout,
        )
        in call_args
    )


def test_main_time_convert_input(mock_commands_time):
    main(argv=["time", "convert", "--input", "file.csv"])

    mock_commands_time.assert_called_once()
    call_args = mock_commands_time.call_args.args
    assert (
        Namespace(
            func=mock_commands_time,
            command="time",
            subcommand="convert",
            client=None,
            input="file.csv",
            output=sys.stdout,
        )
        in call_args
    )


def test_main_time_convert_output(mock_commands_time):
    main(argv=["time", "convert", "--output", "file.csv"])

    mock_commands_time.assert_called_once()
    call_args = mock_commands_time.call_args.args
    assert (
        Namespace(
            func=mock_commands_time,
            command="time",
            subcommand="convert",
            client=None,
            input=sys.stdin,
            output="file.csv",
        )
        in call_args
    )


def test_main_user_create(mock_commands_user):
    main(argv=["user", "create", "username"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="create", username="username", notify=None) in call_args
    )


def test_main_user_create_notify(mock_commands_user):
    main(argv=["user", "create", "username", "--notify", "notification"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="create", username="username", notify="notification")
        in call_args
    )


def test_main_user_create_extras(mock_commands_user):
    main(argv=["user", "create", "username", "extra1", "extra2"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="create", username="username", notify=None) in call_args
    )
    assert "extra1" in call_args
    assert "extra2" in call_args


def test_main_user_create_no_username(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "create"])
        assert mock_commands_user.call_count == 0


def test_main_user_convert(mock_commands_user):
    main(argv=["user", "convert", "username", "contractor"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(
            func=mock_commands_user, command="user", subcommand="convert", username="username", account_type="contractor"
        )
        in call_args
    )


def test_main_user_convert_no_username(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "convert"])
        assert mock_commands_user.call_count == 0


def test_main_user_convert_bad_account_type(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "convert", "username", "account_type"])
        assert mock_commands_user.call_count == 0


def test_main_user_delete(mock_commands_user):
    main(argv=["user", "delete", "username"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="delete", username="username", force=False) in call_args
    )


def test_main_user_delete_force(mock_commands_user):
    main(argv=["user", "delete", "username", "--force"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="delete", username="username", force=True) in call_args
    )


def test_main_user_delete_no_username(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "delete"])
        assert mock_commands_user.call_count == 0


def test_main_user_offboard(mock_commands_user):
    main(argv=["user", "offboard", "username"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="offboard", username="username", alias=None, force=False)
        in call_args
    )


def test_main_user_offboard_force(mock_commands_user):
    main(argv=["user", "offboard", "username", "--force"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="offboard", username="username", alias=None, force=True)
        in call_args
    )


def test_main_user_offboard_with_alias(mock_commands_user):
    main(argv=["user", "offboard", "username", "--alias", "anotheruser"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(
            func=mock_commands_user,
            command="user",
            subcommand="offboard",
            username="username",
            alias="anotheruser",
            force=False,
        )
        in call_args
    )


def test_main_user_offboard_no_username(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "offboard"])
        assert mock_commands_user.call_count == 0


def test_main_user_reset_password(mock_commands_user):
    main(argv=["user", "reset-password", "username"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="reset-password", username="username", notify=None)
        in call_args
    )


def test_main_user_reset_password_notify(mock_commands_user):
    main(argv=["user", "reset-password", "username", "--notify", "notification"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(
            func=mock_commands_user, command="user", subcommand="reset-password", username="username", notify="notification"
        )
        in call_args
    )


def test_main_user_reset_password_no_username(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "reset-password"])
        assert mock_commands_user.call_count == 0


def test_main_user_restore(mock_commands_user):
    main(argv=["user", "restore", "username"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert Namespace(func=mock_commands_user, command="user", subcommand="restore", username="username") in call_args


def test_main_user_restore_no_username(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "restore"])
        assert mock_commands_user.call_count == 0


def test_main_user_signout(mock_commands_user):
    main(argv=["user", "signout", "username"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="signout", username="username", force=False) in call_args
    )


def test_main_user_signout_force(mock_commands_user):
    main(argv=["user", "signout", "username", "--force"])

    mock_commands_user.assert_called_once()
    call_args = mock_commands_user.call_args.args
    assert (
        Namespace(func=mock_commands_user, command="user", subcommand="signout", username="username", force=True) in call_args
    )


def test_main_user_signout_no_username(mock_commands_user):
    with pytest.raises(SystemExit):
        main(argv=["user", "signout"])
        assert mock_commands_user.call_count == 0


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
    assert "compiler-admin:" in captured.out
    assert "GAMADV-XTD3" in captured.out
    assert f"Primary Domain: {DOMAIN}" in captured.out
    assert "WARNING: Config File:" not in captured.err
