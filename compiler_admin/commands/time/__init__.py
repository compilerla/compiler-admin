from argparse import Namespace

from compiler_admin.commands.time.convert import convert  # noqa: F401


def time(args: Namespace, *extra):
    # try to call the subcommand function directly from global (module) symbols
    # if the subcommand function was imported above, it should exist in globals()
    global_env = globals()

    if args.subcommand in global_env:
        cmd_func = global_env[args.subcommand]
        cmd_func(args, *extra)
    else:
        raise NotImplementedError(f"Unknown time subcommand: {args.subcommand}")
