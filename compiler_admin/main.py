import click

from compiler_admin import __version__

from compiler_admin.commands.info import info
from compiler_admin.commands.init import init
from compiler_admin.commands.time import time
from compiler_admin.commands.user import user


@click.group
@click.version_option(__version__, prog_name="compiler-admin")
def main():
    """Compiler's command line interface."""
    pass


main.add_command(init)
main.add_command(info)
main.add_command(time)
main.add_command(user)

if __name__ == "__main__":
    raise SystemExit(main())
