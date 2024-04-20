from argparse import ArgumentParser, _SubParsersAction
import sys

from compiler_admin import __version__ as version
from compiler_admin.commands.info import info
from compiler_admin.commands.init import init
from compiler_admin.commands.time import time
from compiler_admin.commands.user import user
from compiler_admin.commands.user.convert import ACCOUNT_TYPE_OU


def add_sub_cmd(cmd: _SubParsersAction, subcmd, help) -> ArgumentParser:
    """Helper creates a new subcommand parser."""
    return cmd.add_parser(subcmd, help=help)


def add_sub_cmd_username(cmd: _SubParsersAction, subcmd, help) -> ArgumentParser:
    """Helper creates a new subcommand parser with a required username arg."""
    return add_username_arg(add_sub_cmd(cmd, subcmd, help=help))


def add_username_arg(cmd: ArgumentParser) -> ArgumentParser:
    cmd.add_argument("username", help="A Compiler user account name, sans domain.")
    return cmd


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = ArgumentParser(prog="compiler-admin")

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )

    cmd_parsers = parser.add_subparsers(dest="command", help="The command to run")

    info_cmd = add_sub_cmd(cmd_parsers, "info", help="Print configuration and debugging information.")
    info_cmd.set_defaults(func=info)

    init_cmd = add_sub_cmd_username(
        cmd_parsers, "init", help="Initialize a new admin project. This command should be run once before any others."
    )
    init_cmd.add_argument("--gam", action="store_true", help="If provided, initialize a new GAM project.")
    init_cmd.add_argument("--gyb", action="store_true", help="If provided, initialize a new GYB project.")
    init_cmd.set_defaults(func=init)

    time_cmd = add_sub_cmd(cmd_parsers, "time", help="Work with Compiler time entries")
    time_cmd.set_defaults(func=time)
    time_subcmds = time_cmd.add_subparsers("subcommand", help="The time command to run.")

    time_convert = add_sub_cmd(time_subcmds, "convert", help="Convert a time report from one format into another.")
    time_convert.add_argument(
        "--input", default=sys.stdin, help="The path to the source data for conversion. Defaults to stdin."
    )
    time_convert.add_argument(
        "--output", default=sys.stdout, help="The path to the file where converted data should be written. Defaults to stdout."
    )
    time_convert.add_argument("--client", default=None, help="The name of the client to use in converted data.")

    user_cmd = add_sub_cmd(cmd_parsers, "user", help="Work with users in the Compiler org.")
    user_cmd.set_defaults(func=user)
    user_subcmds = user_cmd.add_subparsers(dest="subcommand", help="The user command to run.")

    user_create = add_sub_cmd_username(user_subcmds, "create", help="Create a new user in the Compiler domain.")
    user_create.add_argument("--notify", help="An email address to send the newly created account info.")

    user_convert = add_sub_cmd_username(user_subcmds, "convert", help="Convert a user account to a new type.")
    user_convert.add_argument("account_type", choices=ACCOUNT_TYPE_OU.keys(), help="Target account type for this conversion.")

    user_delete = add_sub_cmd_username(user_subcmds, "delete", help="Delete a user account.")
    user_delete.add_argument("--force", action="store_true", default=False, help="Don't ask for confirmation before deletion.")

    user_offboard = add_sub_cmd_username(user_subcmds, "offboard", help="Offboard a user account.")
    user_offboard.add_argument("--alias", help="Account to assign username as an alias.")
    user_offboard.add_argument(
        "--force", action="store_true", default=False, help="Don't ask for confirmation before offboarding."
    )

    user_reset = add_sub_cmd_username(
        user_subcmds, "reset-password", help="Reset a user's password to a randomly generated string."
    )
    user_reset.add_argument("--notify", help="An email address to send the newly generated password.")

    add_sub_cmd_username(user_subcmds, "restore", help="Restore an email backup from a prior offboarding.")

    user_signout = add_sub_cmd_username(user_subcmds, "signout", help="Signs a user out from all active sessions.")
    user_signout.add_argument("--force", action="store_true", default=False, help="Don't ask for confirmation before signout.")

    if len(argv) == 0:
        argv = ["info"]

    args, extra = parser.parse_known_args(argv)

    if args.func:
        return args.func(args, *extra)
    else:
        raise ValueError("Unrecognized command")


if __name__ == "__main__":
    raise SystemExit(main())
