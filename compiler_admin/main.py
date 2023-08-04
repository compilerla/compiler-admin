import argparse
import sys

from compiler_admin import __version__ as version
from compiler_admin.commands.create import create
from compiler_admin.commands.delete import delete
from compiler_admin.commands.info import info
from compiler_admin.commands.init import init
from compiler_admin.commands.offboard import offboard
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

    def _subcmd(name, help, add_username_arg=False):
        """Helper creates a new subcommand parser."""
        parser = subparsers.add_parser(name, help=help)
        if add_username_arg is True:
            parser.add_argument("username", help="The user's account name, sans domain.")
        return parser

    _subcmd("info", help="Print configuration and debugging information.")

    _subcmd(
        "init",
        help="Initialize a new admin project. This command should be run once before any others.",
        add_username_arg=True,
    )

    _subcmd("create", help="Create a new user in the Compiler domain.", add_username_arg=True)

    _subcmd("delete", help="Delete a user account.", add_username_arg=True)

    _subcmd("offboard", help="Offboard a user account.", add_username_arg=True)

    _subcmd("signout", help="Signs a user out from all active sessions.", add_username_arg=True)

    if len(argv) == 0:
        argv = ["info"]

    args, extra = parser.parse_known_args(argv)

    if args.command == "info":
        return info()
    elif args.command == "create":
        return create(args.username, *extra)
    elif args.command == "delete":
        return delete(args.username)
    elif args.command == "init":
        return init(args.username)
    elif args.command == "offboard":
        return offboard(args.username)
    elif args.command == "signout":
        return signout(args.username)


if __name__ == "__main__":
    raise SystemExit(main())
