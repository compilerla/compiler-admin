from argparse import Namespace

import pytest

from compiler_admin.commands.time import time


def test_time_subcommand_exists(mocker):
    args = Namespace(subcommand="subcmd")
    subcmd = mocker.patch("compiler_admin.commands.time.globals", return_value={"subcmd": mocker.Mock()})

    time(args, 1, 2, 3)

    subcmd.assert_called_once()
    subcmd.return_value["subcmd"].assert_called_once_with(args, 1, 2, 3)


def test_time_subcommand_doesnt_exists(mocker):
    args = Namespace(subcommand="subcmd")
    subcmd = mocker.patch("compiler_admin.commands.time.globals", return_value={})

    with pytest.raises(NotImplementedError, match="Unknown time subcommand: subcmd"):
        time(args, 1, 2, 3)

    subcmd.assert_called_once()
