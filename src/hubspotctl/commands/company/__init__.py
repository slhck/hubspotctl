"""Company commands."""

import click

from hubspotctl.cli import Context, pass_context
from hubspotctl.commands._notes import format_notes, NOTE_COLUMNS
from hubspotctl.output import format_output, print_error, print_info, print_success


def _format_company(c: dict, extra_properties: list[str] | None = None) -> dict:
    """Extract display fields from a company API response."""
    props = c.get("properties", {})
    result = {
        "id": c["id"],
        "name": props.get("name") or "",
        "domain": props.get("domain") or "",
        "industry": props.get("industry") or "",
        "phone": props.get("phone") or "",
        "city": props.get("city") or "",
        "state": props.get("state") or "",
        "country": props.get("country") or "",
        "owner": props.get("hubspot_owner_id") or "",
    }
    for name in extra_properties or []:
        if name not in result:
            result[name] = props.get(name) or ""
    return result


COMPANY_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("domain", "Domain"),
    ("industry", "Industry"),
    ("phone", "Phone"),
    ("city", "City"),
    ("country", "Country"),
]

COMPANY_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("domain", "Domain"),
    ("industry", "Industry"),
    ("phone", "Phone"),
    ("city", "City"),
    ("state", "State"),
    ("country", "Country"),
    ("owner", "Owner ID"),
]


@click.group()
def company() -> None:
    """Company management commands."""
    pass


@company.command("list")
@click.option("--limit", "-l", default=20, help="Number of results (max 100)")
@click.option("--after", help="Pagination cursor")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def list_companies(
    ctx: Context, limit: int, after: str | None, property: tuple[str, ...]
) -> None:
    """List companies."""
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        result = client.list_companies(limit=limit, after=after, properties=props)
    except Exception as e:
        print_error(f"Failed to list companies: {e}")
        return

    companies = result.get("results", [])
    extra = list(property)
    data = [_format_company(c, extra_properties=extra) for c in companies]

    columns = list(COMPANY_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(
        data,
        ctx.format,
        columns=columns,
        title="Companies",
        template="{name} ({domain}) ({id})",
    )

    paging = result.get("paging", {})
    next_after = paging.get("next", {}).get("after")
    if next_after:
        print_info(f"More results available. Use --after {next_after}")


@company.command("show")
@click.argument("company_id")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def show_company(ctx: Context, company_id: str, property: tuple[str, ...]) -> None:
    """Show details of a company."""
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        c = client.get_company(company_id, properties=props)
    except Exception as e:
        print_error(f"Failed to get company: {e}")
        return

    extra = list(property)
    data = _format_company(c, extra_properties=extra)

    columns = list(COMPANY_DETAIL_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(data, ctx.format, columns=columns)


@company.command("search")
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Number of results (max 200)")
@click.option("--after", help="Pagination cursor")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def search_companies(
    ctx: Context,
    query: str,
    limit: int,
    after: str | None,
    property: tuple[str, ...],
) -> None:
    """Search companies by name, domain, etc.

    QUERY is a free-text search across default searchable properties.
    """
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        result = client.search_companies(
            query=query, limit=limit, after=after, properties=props
        )
    except Exception as e:
        print_error(f"Search failed: {e}")
        return

    companies = result.get("results", [])
    extra = list(property)
    data = [_format_company(c, extra_properties=extra) for c in companies]

    columns = list(COMPANY_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(
        data,
        ctx.format,
        columns=columns,
        title=f"Search: {query}",
        template="{name} ({domain}) ({id})",
    )

    total = result.get("total", len(companies))
    paging = result.get("paging", {})
    next_after = paging.get("next", {}).get("after")
    if next_after:
        print_info(f"Showing {len(companies)} of {total}. Use --after {next_after}")


@company.command("create")
@click.option("--name", "-n", required=True, help="Company name")
@click.option("--domain", "-d", help="Company domain")
@click.option("--industry", help="Industry")
@click.option("--phone", help="Phone number")
@click.option("--owner", help="Owner ID")
@click.option(
    "--prop",
    multiple=True,
    help="Additional property as key=value",
)
@pass_context
def create_company(
    ctx: Context,
    name: str,
    domain: str | None,
    industry: str | None,
    phone: str | None,
    owner: str | None,
    prop: tuple[str, ...],
) -> None:
    """Create a new company."""
    client = ctx.ensure_client()

    properties: dict[str, str] = {"name": name}
    if domain:
        properties["domain"] = domain
    if industry:
        properties["industry"] = industry
    if phone:
        properties["phone"] = phone
    if owner:
        properties["hubspot_owner_id"] = owner
    for p in prop:
        key, _, value = p.partition("=")
        if not value:
            print_error(f"Invalid property format: {p} (expected key=value)")
            return
        properties[key] = value

    try:
        c = client.create_company(properties)
        print_success(f"Created company: {c['id']}")
    except Exception as e:
        print_error(f"Failed to create company: {e}")


@company.command("update")
@click.argument("company_id")
@click.option("--name", "-n", help="Company name")
@click.option("--domain", "-d", help="Company domain")
@click.option("--industry", help="Industry")
@click.option("--phone", help="Phone number")
@click.option("--owner", help="Owner ID")
@click.option(
    "--prop",
    multiple=True,
    help="Additional property as key=value",
)
@pass_context
def update_company(
    ctx: Context,
    company_id: str,
    name: str | None,
    domain: str | None,
    industry: str | None,
    phone: str | None,
    owner: str | None,
    prop: tuple[str, ...],
) -> None:
    """Update a company's properties."""
    client = ctx.ensure_client()

    properties: dict[str, str] = {}
    if name:
        properties["name"] = name
    if domain:
        properties["domain"] = domain
    if industry:
        properties["industry"] = industry
    if phone:
        properties["phone"] = phone
    if owner:
        properties["hubspot_owner_id"] = owner
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
        client.update_company(company_id, properties)
        print_success(f"Updated company: {company_id}")
    except Exception as e:
        print_error(f"Failed to update company: {e}")


@company.command("delete")
@click.argument("company_id")
@click.confirmation_option(prompt="Are you sure you want to delete this company?")
@pass_context
def delete_company(ctx: Context, company_id: str) -> None:
    """Delete (archive) a company."""
    client = ctx.ensure_client()

    try:
        client.delete_company(company_id)
        print_success(f"Deleted company: {company_id}")
    except Exception as e:
        print_error(f"Failed to delete company: {e}")


@company.command("add-note")
@click.argument("company_id")
@click.option("--body", "-b", required=True, help="Note text")
@pass_context
def add_note(ctx: Context, company_id: str, body: str) -> None:
    """Add a note to a company."""
    client = ctx.ensure_client()

    try:
        note = client.add_note("companies", company_id, body)
        print_success(f"Added note {note['id']} to company {company_id}")
    except Exception as e:
        print_error(f"Failed to add note: {e}")


@company.command("notes")
@click.argument("company_id")
@pass_context
def list_notes(ctx: Context, company_id: str) -> None:
    """List notes for a company."""
    client = ctx.ensure_client()

    try:
        notes = client.list_notes("companies", company_id)
    except Exception as e:
        print_error(f"Failed to list notes: {e}")
        return

    data = format_notes(notes)
    format_output(
        data,
        ctx.format,
        columns=NOTE_COLUMNS,
        title=f"Notes for company {company_id}",
        template="{id}: {body}",
    )


@company.command("delete-note")
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
