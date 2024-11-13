import click

from compiler_admin import __version__

from compiler_admin.commands_click.info import info
from compiler_admin.commands_click.init import init
from compiler_admin.commands_click.time import time
from compiler_admin.commands_click.user import user


@click.group
@click.version_option(__version__, prog_name="compiler-admin")
def cli():
    """Compiler's command line interface."""
    pass


cli.add_command(init)
cli.add_command(info)
cli.add_command(time)
cli.add_command(user)

if __name__ == "__main__":
    cli()
