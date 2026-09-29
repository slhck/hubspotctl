"""Shared email subcommands for contacts, companies, and deals.

Emails are logged as engagements on CRM records. The HubSpot API cannot send
emails this way; it only records them on the timeline.
"""

import json
import re
from datetime import datetime
from typing import IO

import click

from hubspotctl.cli import Context, pass_context
from hubspotctl.output import format_output, print_error, print_success

# Singular labels used in human-facing messages.
SINGULAR = {
    "contacts": "contact",
    "companies": "company",
    "deals": "deal",
}

# CLI direction names mapped to hs_email_direction values
DIRECTIONS = {
    "outgoing": "EMAIL",
    "incoming": "INCOMING_EMAIL",
    "forwarded": "FORWARDED_EMAIL",
}

STATUSES = ["sent", "scheduled", "sending", "bounced", "failed"]

EMAIL_COLUMNS = [
    ("id", "ID"),
    ("timestamp", "Timestamp"),
    ("direction", "Direction"),
    ("from", "From"),
    ("to", "To"),
    ("subject", "Subject"),
]

EMAIL_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("timestamp", "Timestamp"),
    ("direction", "Direction"),
    ("status", "Status"),
    ("from", "From"),
    ("to", "To"),
    ("cc", "Cc"),
    ("bcc", "Bcc"),
    ("subject", "Subject"),
    ("body", "Body"),
]


def _html_to_text(html: str) -> str:
    """Convert an HTML email body to plain text."""
    text = re.sub(r"(?i)<br\s*/?>|</p>|</div>", "\n", html)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _join_addresses(value: str | None) -> str:
    """Format a semicolon-separated address list for display."""
    return ", ".join(a for a in (value or "").split(";") if a)


def format_email(e: dict) -> dict:
    """Extract display fields from an email API response."""
    props = e.get("properties", {})
    direction = props.get("hs_email_direction") or ""
    direction_names = {v: k for k, v in DIRECTIONS.items()}
    body = props.get("hs_email_text") or _html_to_text(props.get("hs_email_html") or "")
    return {
        "id": e["id"],
        "timestamp": props.get("hs_timestamp") or "",
        "direction": direction_names.get(direction, direction),
        "status": props.get("hs_email_status") or "",
        "from": props.get("hs_email_from_email") or "",
        "to": _join_addresses(props.get("hs_email_to_email")),
        "cc": _join_addresses(props.get("hs_email_cc_email")),
        "bcc": _join_addresses(props.get("hs_email_bcc_email")),
        "subject": props.get("hs_email_subject") or "",
        "body": body.strip(),
    }


def _parse_timestamp(value: str | None) -> str:
    """Convert an ISO 8601 date or datetime to epoch milliseconds.

    Naive values are interpreted in local time. Defaults to now.
    """
    dt = datetime.fromisoformat(value) if value else datetime.now()
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return str(int(dt.timestamp() * 1000))


def build_email_properties(
    subject: str,
    body: str,
    html: bool,
    direction: str,
    status: str,
    sender: str | None,
    to: tuple[str, ...],
    cc: tuple[str, ...],
    bcc: tuple[str, ...],
    timestamp: str | None,
    owner: str | None,
) -> dict[str, str]:
    """Build the HubSpot properties for logging an email."""
    headers: dict = {
        "to": [{"email": a} for a in to],
        "cc": [{"email": a} for a in cc],
        "bcc": [{"email": a} for a in bcc],
    }
    if sender:
        headers["from"] = {"email": sender}
    properties = {
        "hs_timestamp": _parse_timestamp(timestamp),
        "hs_email_direction": DIRECTIONS[direction],
        "hs_email_status": status,
        "hs_email_subject": subject,
        "hs_email_headers": json.dumps(headers),
    }
    if html:
        properties["hs_email_html"] = body
        properties["hs_email_text"] = _html_to_text(body)
    else:
        properties["hs_email_text"] = body
    if owner:
        properties["hubspot_owner_id"] = owner
    return properties


def register_email_commands(group: click.Group, object_type: str) -> None:
    """Add the email subcommands to a contact, company, or deal group."""
    singular = SINGULAR[object_type]

    @group.command(
        "add-email",
        help=f"Log an email on a {singular}.\n\n"
        "This records the email in HubSpot; it does not send it.",
    )
    @click.argument("object_id", metavar=f"{singular.upper()}_ID")
    @click.option("--subject", "-s", required=True, help="Email subject")
    @click.option("--body", "-b", help="Email body")
    @click.option(
        "--body-file",
        type=click.File("r"),
        help="Read the email body from a file ('-' for stdin)",
    )
    @click.option("--html", is_flag=True, help="Treat the body as HTML")
    @click.option(
        "--direction",
        type=click.Choice(list(DIRECTIONS)),
        default="outgoing",
        show_default=True,
        help="Email direction",
    )
    @click.option(
        "--status",
        type=click.Choice(STATUSES),
        default="sent",
        show_default=True,
        help="Send status",
    )
    @click.option("--from", "sender", help="Sender email address")
    @click.option("--to", multiple=True, help="Recipient email address (repeatable)")
    @click.option("--cc", multiple=True, help="Cc email address (repeatable)")
    @click.option("--bcc", multiple=True, help="Bcc email address (repeatable)")
    @click.option(
        "--timestamp",
        "-t",
        help="Time the email was sent, as ISO 8601 (default: now)",
    )
    @click.option("--owner", help="Owner ID (see 'deal owners')")
    @pass_context
    def add_email(
        ctx: Context,
        object_id: str,
        subject: str,
        body: str | None,
        body_file: IO[str] | None,
        html: bool,
        direction: str,
        status: str,
        sender: str | None,
        to: tuple[str, ...],
        cc: tuple[str, ...],
        bcc: tuple[str, ...],
        timestamp: str | None,
        owner: str | None,
    ) -> None:
        if (body is None) == (body_file is None):
            print_error("Specify exactly one of --body or --body-file")
            return
        text = body if body is not None else body_file.read()  # type: ignore[union-attr]

        try:
            properties = build_email_properties(
                subject,
                text,
                html,
                direction,
                status.upper(),
                sender,
                to,
                cc,
                bcc,
                timestamp,
                owner,
            )
        except ValueError as e:
            print_error(f"Invalid timestamp: {e}")
            return

        client = ctx.ensure_client()
        try:
            email = client.add_email(object_type, object_id, properties)
            print_success(f"Logged email {email['id']} on {singular} {object_id}")
        except Exception as e:
            print_error(f"Failed to log email: {e}")

    @group.command("emails", help=f"List emails logged on a {singular}, newest first.")
    @click.argument("object_id", metavar=f"{singular.upper()}_ID")
    @pass_context
    def list_emails(ctx: Context, object_id: str) -> None:
        client = ctx.ensure_client()

        try:
            emails = client.list_emails(object_type, object_id)
        except Exception as e:
            print_error(f"Failed to list emails: {e}")
            return

        data = [format_email(e) for e in emails]
        format_output(
            data,
            ctx.format,
            columns=EMAIL_COLUMNS,
            title=f"Emails for {singular} {object_id}",
            template="{id}: [{timestamp}] {from} -> {to}: {subject}",
        )

    @group.command("show-email")
    @click.argument("email_id")
    @pass_context
    def show_email(ctx: Context, email_id: str) -> None:
        """Show an email, including its body."""
        client = ctx.ensure_client()

        try:
            email = client.get_email(email_id)
        except Exception as e:
            print_error(f"Failed to get email: {e}")
            return

        format_output(
            format_email(email),
            ctx.format,
            columns=EMAIL_DETAIL_COLUMNS,
            template="From: {from}\nTo: {to}\nDate: {timestamp}\n"
            "Subject: {subject}\n\n{body}",
        )

    @group.command("delete-email")
    @click.argument("email_id")
    @click.confirmation_option(prompt="Are you sure you want to delete this email?")
    @pass_context
    def delete_email(ctx: Context, email_id: str) -> None:
        """Delete a logged email."""
        client = ctx.ensure_client()

        try:
            client.delete_email(email_id)
            print_success(f"Deleted email: {email_id}")
        except Exception as e:
            print_error(f"Failed to delete email: {e}")
