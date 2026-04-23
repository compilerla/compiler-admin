import click

from compiler_admin.services.google import GoogleOrgs


@click.command()
def orgs(**kwargs):
    """List org units in the Compiler Google workspace."""
    output = GoogleOrgs().get(**kwargs)
    click.echo(output)
