import click

from compiler_admin.services.google import get_org_units


@click.command()
def orgs(**kwargs):
    """List org units in the Compiler Google workspace."""
    output = get_org_units(**kwargs)
    click.echo(output)
