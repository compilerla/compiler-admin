from argparse import Namespace

from compiler_admin.commands.user.alumni import alumni  # noqa: F401
from compiler_admin.commands.user.create import create  # noqa: F401
from compiler_admin.commands.user.convert import convert  # noqa: F401
from compiler_admin.commands.user.delete import delete  # noqa: F401
from compiler_admin.commands.user.offboard import offboard  # noqa: F401
from compiler_admin.commands.user.reset import reset  # noqa: F401
from compiler_admin.commands.user.restore import restore  # noqa: F401
from compiler_admin.commands.user.signout import signout  # noqa: F401


def user(args: Namespace, *extra):
    # try to call the subcommand function directly from global (module) symbols
    # if the subcommand function was imported above, it should exist in globals()
    global_env = globals()

    if args.subcommand in global_env:
        cmd_func = global_env[args.subcommand]
        cmd_func(args, *extra)
    else:
        raise NotImplementedError(f"Unknown user subcommand: {args.subcommand}")
