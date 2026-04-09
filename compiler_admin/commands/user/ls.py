import click

from compiler_admin.services.google import CallGAMCommand

USER_SYSTEMS = ["google"]


@click.command()
@click.option(
    "--system",
    help="The system from which to list accounts.",
    type=click.Choice(USER_SYSTEMS, case_sensitive=False),
    default="google",
)
def ls(system: str, **kwargs):
    """Lists users in the Compiler workspace."""
    match system:
        case "google":
            ls_google(**kwargs)
        case _:
            click.echo(f"Unknown user system: {system}")


def ls_google(**kwargs):
    click.echo("Listing users in Compiler Google workspace")

    command = ("print", "users")
    CallGAMCommand(command)
