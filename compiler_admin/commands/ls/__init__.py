import click

from compiler_admin.commands.ls.clients import clients
from compiler_admin.commands.ls.groups import groups
from compiler_admin.commands.ls.orgs import orgs
from compiler_admin.commands.ls.project_users import project_users
from compiler_admin.commands.ls.projects import projects
from compiler_admin.commands.ls.users import users


@click.group
def ls():
    """Print information about the Compiler org."""
    pass


ls.add_command(clients)
ls.add_command(groups)
ls.add_command(orgs)
ls.add_command(project_users)
ls.add_command(projects)
ls.add_command(users)
