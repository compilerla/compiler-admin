from argparse import Namespace

from compiler_admin.commands.user.create import create  # noqa: F401
from compiler_admin.commands.user.convert import convert  # noqa: F401
from compiler_admin.commands.user.delete import delete  # noqa: F401
from compiler_admin.commands.user.offboard import offboard  # noqa: F401
from compiler_admin.commands.user.reset_password import reset_password  # noqa: F401
from compiler_admin.commands.user.restore import restore  # noqa: F401
from compiler_admin.commands.user.signout import signout  # noqa: F401


def user(args: Namespace, *extra):
    # try to call the subcommand function directly from local symbols
    # if the subcommand function was imported above, it should exist in locals()
    if args.subcommand in locals():
        locals()[args.subcommand](args, *extra)
    else:
        raise ValueError(f"Unknown user subcommand: {args.subcommand}")
