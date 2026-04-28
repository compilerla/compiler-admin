import click

from compiler_admin import Result
from compiler_admin.services.google import GoogleAccount, GoogleGroups, GoogleOrgs


@click.command()
@click.option("-f", "--force", is_flag=True, help="Don't ask for confirmation.")
@click.argument("username")
@click.argument("account_type", type=click.Choice(GoogleOrgs.ORG_UNITS.keys(), case_sensitive=False))
@click.pass_context
def convert(ctx: click.Context, username: str, account_type: str, **kwargs):
    """Convert a user of one type to another."""
    account = GoogleAccount(username)
    groups = GoogleGroups()
    orgs = GoogleOrgs()

    if not account.exists():
        click.echo(f"User does not exist: {account}")
        raise SystemExit(Result.FAILURE)

    ou = orgs[account_type]
    click.echo(f"User exists, converting to: {ou} for {account}")

    if ou == orgs.OU_CONTRACTORS:
        if account.is_partner():
            groups.remove_user(account, groups.GROUP_PARTNERS)
            groups.remove_user(account, groups.GROUP_STAFF)
        elif account.is_staff():
            groups.remove_user(account, groups.GROUP_STAFF)

    elif ou == orgs.OU_STAFF:
        if account.is_partner():
            groups.remove_user(account, groups.GROUP_PARTNERS)
        elif account.is_staff():
            click.echo(f"User is already staff: {account}")
            raise SystemExit(Result.FAILURE)
        groups.add_user(account, groups.GROUP_STAFF)

    elif ou == orgs.OU_PARTNERS:
        if account.is_partner():
            click.echo(f"User is already partner: {account}")
            raise SystemExit(Result.FAILURE)
        if not account.is_staff():
            groups.add_user(account, groups.GROUP_STAFF)
        groups.add_user(account, groups.GROUP_PARTNERS)

    orgs.move_user(account, ou)

    click.echo(f"Account conversion complete for: {account}")
