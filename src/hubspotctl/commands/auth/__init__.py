"""Authentication commands."""

import click

from hubspotctl.cli import Context, pass_context
from hubspotctl.output import print_error, print_info, print_success


@click.group()
def auth() -> None:
    """Authentication commands."""
    pass


@auth.command("login")
@click.option("--token", prompt=False, help="HubSpot private app access token")
@pass_context
def login(ctx: Context, token: str | None) -> None:
    """Set up authentication with HubSpot.

    Uses a private app access token. Create one at:
    Settings > Integrations > Private Apps
    """
    if not token:
        print_info(
            "Create a private app at: HubSpot Settings > Integrations > Private Apps"
        )
        print_info(
            "Required scopes: crm.objects.contacts.read, "
            "crm.objects.contacts.write, crm.objects.companies.read, "
            "crm.objects.companies.write, crm.objects.deals.read, "
            "crm.objects.deals.write, crm.objects.owners.read "
            "(and optionally *.sensitive.read, "
            "*.highly_sensitive.read, crm.schemas.*.read/write)"
        )
        token = click.prompt("Enter your access token")

    ctx.config.set_token(token)
    print_success("Token saved")

    # Verify credentials
    try:
        client = ctx.ensure_client()
        info = client.get_me()
        portal_id = info.get("portalId", "unknown")
        print_success(f"Authenticated (portal ID: {portal_id})")
    except Exception as e:
        print_error(f"Authentication failed: {e}")


@auth.command("status")
@pass_context
def status(ctx: Context) -> None:
    """Check authentication status."""
    if not ctx.config.is_configured():
        print_error("Not authenticated. Run 'hubspotctl auth login' first.")
        return

    try:
        client = ctx.ensure_client()
        info = client.get_me()
        portal_id = info.get("portalId", "unknown")
        print_success(f"Authenticated (portal ID: {portal_id})")
    except Exception as e:
        print_error(f"Authentication error: {e}")


@auth.command("logout")
@pass_context
def logout(ctx: Context) -> None:
    """Remove stored credentials."""
    import keyring
    from hubspotctl.config import SERVICE_NAME

    try:
        keyring.delete_password(SERVICE_NAME, f"{ctx.profile}:token")
    except keyring.errors.PasswordDeleteError:
        pass

    print_success("Credentials removed")
