import argparse
import sys

from compiler_admin import __version__ as version
from compiler_admin.services.google import CallGAMCommand


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

    parser.parse_args(argv)

    print(f"compiler-admin: {version}")

    return CallGAMCommand(["version"])


if __name__ == "__main__":
    raise SystemExit(main())
