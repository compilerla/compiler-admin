import argparse
import sys

from compiler_admin import __version__ as version
from compiler_admin.commands.create import create
from compiler_admin.commands.convert import ACCOUNT_TYPE_OU, convert
from compiler_admin.commands.delete import delete
from compiler_admin.commands.info import info
from compiler_admin.commands.init import init
from compiler_admin.commands.offboard import offboard
from compiler_admin.commands.reset_password import reset_password
from compiler_admin.commands.restore import restore
from compiler_admin.commands.signout import signout


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="compiler-admin")

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )

    subparsers = parser.add_subparsers(dest="command")

    def _subcmd(name, help, add_username_arg=True) -> argparse.ArgumentParser:
        """Helper creates a new subcommand parser."""
        parser = subparsers.add_parser(name, help=help)
        if add_username_arg is True:
            parser.add_argument("username", help="A Compiler user account name, sans domain.")
        return parser

    _subcmd("info", help="Print configuration and debugging information.", add_username_arg=False)

    init_parser = _subcmd(
        "init",
        help="Initialize a new admin project. This command should be run once before any others.",
    )
    init_parser.add_argument("--gam", action="store_true", help="If provided, initialize a new GAM project.")
    init_parser.add_argument("--gyb", action="store_true", help="If provided, initialize a new GYB project.")

    create_parser = _subcmd("create", help="Create a new user in the Compiler domain.")
    create_parser.add_argument("--notify", help="An email address to send the newly created account info.")

    convert_parser = _subcmd("convert", help="Convert a user account to a new type.")
    convert_parser.add_argument(
        "account_type", choices=ACCOUNT_TYPE_OU.keys(), help="Target account type for this conversion."
    )

    delete_parser = _subcmd("delete", help="Delete a user account.")
    delete_parser.add_argument(
        "--force", action="store_true", default=False, help="Don't ask for confirmation before deletion."
    )

    offboard_parser = _subcmd("offboard", help="Offboard a user account.")
    offboard_parser.add_argument("--alias", help="Account to assign username as an alias.")
    offboard_parser.add_argument(
        "--force", action="store_true", default=False, help="Don't ask for confirmation before offboarding."
    )

    reset_parser = _subcmd("reset-password", help="Reset a user's password to a randomly generated string.")
    reset_parser.add_argument("--notify", help="An email address to send the newly generated password.")

    _subcmd("restore", help="Restore an email backup from a prior offboarding.")

    signout_parser = _subcmd("signout", help="Signs a user out from all active sessions.")
    signout_parser.add_argument(
        "--force", action="store_true", default=False, help="Don't ask for confirmation before signout."
    )

    if len(argv) == 0:
        argv = ["info"]

    args, extra = parser.parse_known_args(argv)

    if args.command == "info":
        return info()
    elif args.command == "create":
        return create(args, *extra)
    elif args.command == "convert":
        return convert(args)
    elif args.command == "delete":
        return delete(args)
    elif args.command == "init":
        return init(args)
    elif args.command == "offboard":
        return offboard(args)
    elif args.command == "restore":
        return restore(args)
    elif args.command == "reset-password":
        return reset_password(args)
    elif args.command == "signout":
        return signout(args)


if __name__ == "__main__":
    raise SystemExit(main())
