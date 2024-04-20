from argparse import Namespace

from compiler_admin.commands.time import convert  # noqa: F401


def time(args: Namespace, *extra):
    # try to call the subcommand function directly from local symbols
    # if the subcommand function was imported above, it should exist in locals()
    if args.subcommand in locals():
        locals()[args.subcommand](args, *extra)
    else:
        raise NotImplementedError(f"Unknown time subcommand: {args.subcommand}")
