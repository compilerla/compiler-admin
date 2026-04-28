import click

from compiler_admin import __version__ as version
from compiler_admin.services.google import GoogleService


@click.command()
def info():
    """Print information about the configured environment."""
    click.echo(f"compiler-admin, version {version}")

    google = GoogleService()

    google.gam_command(("version",))
    google.gam_command(("info", "domain"))
    google.gyb_command(("--version",))
