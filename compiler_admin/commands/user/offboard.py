import click

from compiler_admin import Result
from compiler_admin.commands.user.deactivate import deactivate
from compiler_admin.commands.user.delete import delete
from compiler_admin.services.google import GoogleAccount, GoogleArchive, GoogleUsers


@click.command()
@click.option("-a", "--alias", help="Another account to assign username as an alias.")
@click.option("-d", "--delete", "_delete", is_flag=True, help="Also delete the account.")
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.option("-n", "--notify", help="An email address to send the new password notification.")
@click.argument("username")
@click.pass_context
def offboard(ctx: click.Context, username: str, alias: str = "", _delete: bool = False, force: bool = False, **kwargs):
    """Fully offboard a user from Compiler.

    Deactivate, back up email, transfer Calendar/Drive, and optionally delete.
    """
    account = GoogleAccount(username)
    google_users = GoogleUsers()
    google_archive = GoogleArchive()

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    alias_account = None
    if alias:
        alias_account = GoogleAccount(alias)
        if not alias_account.exists():
            click.echo(f"Alias target user does not exist: {alias_account}")
            raise SystemExit(Result.FAILURE)

    if not force:
        cont = input(f"Offboard account {account} {' (assigning alias to ' + alias_account + ')' if alias else ''}? (Y/n): ")
        if not cont.lower().startswith("y"):
            click.echo("Aborting offboard.")
            raise SystemExit(Result.SUCCESS)

    click.echo(f"User exists, offboarding: {account}")

    # call the deactivate command
    ctx.forward(deactivate)

    click.echo("Backing up email")
    google_archive.create_email_backup(account)

    click.echo("Starting Drive and Calendar transfer")
    google_archive.archive_content(account)

    google_archive.await_archive_completion(account, lambda: click.echo("Transfer in progress"))
    click.echo("Transfer complete")

    click.echo("Deprovisioning POP/IMAP")
    google_users.deprovision_popimap(account)

    # call the delete command
    if _delete:
        ctx.forward(delete)

    if alias_account:
        click.echo(f"Adding an alias to account: {alias_account}")
        alias_account.add_email_alias(account)

    click.echo(f"Offboarding for user complete: {account}")
