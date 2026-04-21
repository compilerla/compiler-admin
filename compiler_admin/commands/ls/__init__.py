import click

from compiler_admin.commands.ls.groups import groups
from compiler_admin.commands.ls.users import users


@click.group
def ls():
    """Print information about the Compiler org."""
    pass


ls.add_command(groups)
ls.add_command(users)
