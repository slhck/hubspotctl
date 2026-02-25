"""Main CLI entry point."""

from __future__ import annotations

import os
import sys

import click

from hubspotctl import __version__
from hubspotctl.client import HubSpotClient
from hubspotctl.config import Config
from hubspotctl.output import OutputFormat, print_error


class Context:
    """CLI context object holding shared state."""

    def __init__(self) -> None:
        self.profile = os.environ.get("HUBSPOTCTL_PROFILE", "default")
        self.config = Config(self.profile)
        self.client: HubSpotClient | None = None
        self.format = OutputFormat.TABLE

    def ensure_client(self) -> HubSpotClient:
        """Ensure we have an authenticated client."""
        if self.client is None:
            token = self.config.get_token()

            if not token:
                print_error("Not authenticated. Run 'hubspotctl auth login' first.")
                sys.exit(1)

            self.client = HubSpotClient(token)

        return self.client


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.version_option(version=__version__, prog_name="hubspotctl")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "csv", "plain"]),
    default="table",
    help="Output format",
)
@click.option(
    "--profile",
    "-p",
    envvar="HUBSPOTCTL_PROFILE",
    default="default",
    help="Configuration profile to use",
)
@pass_context
def main(ctx: Context, format: str, profile: str) -> None:
    """hubspotctl - Manage your HubSpot CRM from the command line."""
    ctx.format = OutputFormat(format)
    ctx.profile = profile
    ctx.config = Config(profile)


def _register_commands() -> None:
    """Register command groups with the main CLI."""
    from hubspotctl.commands import auth, company, contact, deal

    main.add_command(auth.auth)
    main.add_command(company.company)
    main.add_command(contact.contact)
    main.add_command(deal.deal)


_register_commands()


if __name__ == "__main__":
    main()
