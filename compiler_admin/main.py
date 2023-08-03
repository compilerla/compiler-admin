import argparse
import sys

from compiler_admin import __version__ as version
from compiler_admin.commands.info import info
from compiler_admin.commands.init import init


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

    def _subcmd(name, help):
        parser = subparsers.add_parser(name, help=help)
        return parser

    _subcmd("info", help="Print configuration and debugging information.")

    init_parser = _subcmd("init", help="Initialize a new admin project. This command should be run once before any others.")
    init_parser.add_argument("admin_user")

    if len(argv) == 0:
        argv = ["info"]

    args = parser.parse_args(argv)

    if args.command == "info":
        return info()
    elif args.command == "init":
        return init(args.admin_user)


if __name__ == "__main__":
    raise SystemExit(main())
