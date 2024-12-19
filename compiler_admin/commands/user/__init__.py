import click

from compiler_admin.commands.user.alumni import alumni
from compiler_admin.commands.user.convert import convert
from compiler_admin.commands.user.create import create
from compiler_admin.commands.user.delete import delete
from compiler_admin.commands.user.offboard import offboard
from compiler_admin.commands.user.reset import reset
from compiler_admin.commands.user.restore import restore
from compiler_admin.commands.user.signout import signout


@click.group
def user():
    """
    Work with users in the Compiler org.
    """
    pass


user.add_command(alumni)
user.add_command(convert)
user.add_command(create)
user.add_command(delete)
user.add_command(offboard)
user.add_command(reset)
user.add_command(restore)
user.add_command(signout)
