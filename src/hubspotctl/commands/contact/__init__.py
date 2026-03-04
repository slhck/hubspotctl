"""Contact commands."""

import click

from hubspotctl.cli import Context, pass_context
from hubspotctl.commands._notes import format_notes, NOTE_COLUMNS
from hubspotctl.output import format_output, print_error, print_success, print_info


def _format_contact(c: dict, extra_properties: list[str] | None = None) -> dict:
    """Extract display fields from a contact API response."""
    props = c.get("properties", {})
    result = {
        "id": c["id"],
        "email": props.get("email") or "",
        "firstname": props.get("firstname") or "",
        "lastname": props.get("lastname") or "",
        "phone": props.get("phone") or "",
        "company": props.get("company") or "",
        "jobtitle": props.get("jobtitle") or "",
        "lifecyclestage": props.get("lifecyclestage") or "",
    }
    for name in extra_properties or []:
        if name not in result:
            result[name] = props.get(name) or ""
    return result


CONTACT_COLUMNS = [
    ("id", "ID"),
    ("firstname", "First Name"),
    ("lastname", "Last Name"),
    ("email", "Email"),
    ("phone", "Phone"),
    ("company", "Company"),
]

CONTACT_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("firstname", "First Name"),
    ("lastname", "Last Name"),
    ("email", "Email"),
    ("phone", "Phone"),
    ("company", "Company"),
    ("jobtitle", "Job Title"),
    ("lifecyclestage", "Lifecycle Stage"),
]


@click.group()
def contact() -> None:
    """Contact management commands."""
    pass


@contact.command("list")
@click.option("--limit", "-l", default=20, help="Number of results (max 100)")
@click.option("--after", help="Pagination cursor")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def list_contacts(
    ctx: Context, limit: int, after: str | None, property: tuple[str, ...]
) -> None:
    """List contacts."""
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        result = client.list_contacts(limit=limit, after=after, properties=props)
    except Exception as e:
        print_error(f"Failed to list contacts: {e}")
        return

    contacts = result.get("results", [])
    extra = list(property)
    data = [_format_contact(c, extra_properties=extra) for c in contacts]

    columns = list(CONTACT_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(
        data,
        ctx.format,
        columns=columns,
        title="Contacts",
        template="{firstname} {lastname} <{email}> ({id})",
    )

    paging = result.get("paging", {})
    next_after = paging.get("next", {}).get("after")
    if next_after:
        print_info(f"More results available. Use --after {next_after}")


@contact.command("show")
@click.argument("contact_id")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def show_contact(ctx: Context, contact_id: str, property: tuple[str, ...]) -> None:
    """Show details of a contact.

    CONTACT_ID can be a numeric ID or an email address.
    """
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        if "@" in contact_id:
            c = client.get_contact_by_email(contact_id, properties=props)
        else:
            c = client.get_contact(contact_id, properties=props)
    except Exception as e:
        print_error(f"Failed to get contact: {e}")
        return

    extra = list(property)
    data = _format_contact(c, extra_properties=extra)

    columns = list(CONTACT_DETAIL_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(data, ctx.format, columns=columns)


@contact.command("search")
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Number of results (max 200)")
@click.option("--after", help="Pagination cursor")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def search_contacts(
    ctx: Context,
    query: str,
    limit: int,
    after: str | None,
    property: tuple[str, ...],
) -> None:
    """Search contacts by name, email, phone, etc.

    QUERY is a free-text search across default searchable properties.
    """
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        result = client.search_contacts(
            query=query, limit=limit, after=after, properties=props
        )
    except Exception as e:
        print_error(f"Search failed: {e}")
        return

    contacts = result.get("results", [])
    extra = list(property)
    data = [_format_contact(c, extra_properties=extra) for c in contacts]

    columns = list(CONTACT_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(
        data,
        ctx.format,
        columns=columns,
        title=f"Search: {query}",
        template="{firstname} {lastname} <{email}> ({id})",
    )

    total = result.get("total", len(contacts))
    paging = result.get("paging", {})
    next_after = paging.get("next", {}).get("after")
    if next_after:
        print_info(f"Showing {len(contacts)} of {total}. Use --after {next_after}")


@contact.command("create")
@click.option("--email", "-e", required=True, help="Email address")
@click.option("--firstname", "-f", help="First name")
@click.option("--lastname", "-l", help="Last name")
@click.option("--phone", help="Phone number")
@click.option("--company", help="Company name")
@click.option("--jobtitle", help="Job title")
@click.option(
    "--prop",
    multiple=True,
    help="Additional property as key=value",
)
@pass_context
def create_contact(
    ctx: Context,
    email: str,
    firstname: str | None,
    lastname: str | None,
    phone: str | None,
    company: str | None,
    jobtitle: str | None,
    prop: tuple[str, ...],
) -> None:
    """Create a new contact."""
    client = ctx.ensure_client()

    properties: dict[str, str] = {"email": email}
    if firstname:
        properties["firstname"] = firstname
    if lastname:
        properties["lastname"] = lastname
    if phone:
        properties["phone"] = phone
    if company:
        properties["company"] = company
    if jobtitle:
        properties["jobtitle"] = jobtitle
    for p in prop:
        key, _, value = p.partition("=")
        if not value:
            print_error(f"Invalid property format: {p} (expected key=value)")
            return
        properties[key] = value

    try:
        c = client.create_contact(properties)
        print_success(f"Created contact: {c['id']}")
    except Exception as e:
        print_error(f"Failed to create contact: {e}")


@contact.command("update")
@click.argument("contact_id")
@click.option("--email", "-e", help="Email address")
@click.option("--firstname", "-f", help="First name")
@click.option("--lastname", "-l", help="Last name")
@click.option("--phone", help="Phone number")
@click.option("--company", help="Company name")
@click.option("--jobtitle", help="Job title")
@click.option(
    "--prop",
    multiple=True,
    help="Additional property as key=value",
)
@pass_context
def update_contact(
    ctx: Context,
    contact_id: str,
    email: str | None,
    firstname: str | None,
    lastname: str | None,
    phone: str | None,
    company: str | None,
    jobtitle: str | None,
    prop: tuple[str, ...],
) -> None:
    """Update a contact's properties.

    CONTACT_ID can be a numeric ID or an email address (with --id-property email).
    """
    client = ctx.ensure_client()

    properties: dict[str, str] = {}
    if email:
        properties["email"] = email
    if firstname:
        properties["firstname"] = firstname
    if lastname:
        properties["lastname"] = lastname
    if phone:
        properties["phone"] = phone
    if company:
        properties["company"] = company
    if jobtitle:
        properties["jobtitle"] = jobtitle
    for p in prop:
        key, _, value = p.partition("=")
        if not value:
            print_error(f"Invalid property format: {p} (expected key=value)")
            return
        properties[key] = value

    if not properties:
        print_error("No updates specified")
        return

    try:
        client.update_contact(contact_id, properties)
        print_success(f"Updated contact: {contact_id}")
    except Exception as e:
        print_error(f"Failed to update contact: {e}")


@contact.command("delete")
@click.argument("contact_id")
@click.confirmation_option(prompt="Are you sure you want to delete this contact?")
@pass_context
def delete_contact(ctx: Context, contact_id: str) -> None:
    """Delete (archive) a contact."""
    client = ctx.ensure_client()

    try:
        client.delete_contact(contact_id)
        print_success(f"Deleted contact: {contact_id}")
    except Exception as e:
        print_error(f"Failed to delete contact: {e}")


@contact.command("add-note")
@click.argument("contact_id")
@click.option("--body", "-b", required=True, help="Note text")
@pass_context
def add_note(ctx: Context, contact_id: str, body: str) -> None:
    """Add a note to a contact."""
    client = ctx.ensure_client()

    try:
        note = client.add_note("contacts", contact_id, body)
        print_success(f"Added note {note['id']} to contact {contact_id}")
    except Exception as e:
        print_error(f"Failed to add note: {e}")


@contact.command("notes")
@click.argument("contact_id")
@pass_context
def list_notes(ctx: Context, contact_id: str) -> None:
    """List notes for a contact."""
    client = ctx.ensure_client()

    try:
        notes = client.list_notes("contacts", contact_id)
    except Exception as e:
        print_error(f"Failed to list notes: {e}")
        return

    data = format_notes(notes)
    format_output(
        data,
        ctx.format,
        columns=NOTE_COLUMNS,
        title=f"Notes for contact {contact_id}",
        template="{id}: {body}",
    )


@contact.command("delete-note")
@click.argument("note_id")
@click.confirmation_option(prompt="Are you sure you want to delete this note?")
@pass_context
def delete_note(ctx: Context, note_id: str) -> None:
    """Delete a note."""
    client = ctx.ensure_client()

    try:
        client.delete_note(note_id)
        print_success(f"Deleted note: {note_id}")
    except Exception as e:
        print_error(f"Failed to delete note: {e}")
