"""Deal commands."""

import click

from hubspotctl.cli import Context, pass_context
from hubspotctl.commands._associations import (
    change_associations,
    show_associations,
    show_labels,
)
from hubspotctl.commands._filters import parse_filters
from hubspotctl.commands._merge import merge_records
from hubspotctl.commands._notes import format_notes, NOTE_COLUMNS
from hubspotctl.output import format_output, print_error, print_success, print_info


def _format_deal(d: dict, extra_properties: list[str] | None = None) -> dict:
    """Extract display fields from a deal API response."""
    props = d.get("properties", {})
    result = {
        "id": d["id"],
        "dealname": props.get("dealname") or "",
        "amount": props.get("amount") or "",
        "dealstage": props.get("dealstage") or "",
        "pipeline": props.get("pipeline") or "",
        "closedate": props.get("closedate") or "",
        "owner": props.get("hubspot_owner_id") or "",
    }
    for name in extra_properties or []:
        if name not in result:
            result[name] = props.get(name) or ""
    return result


DEAL_COLUMNS = [
    ("id", "ID"),
    ("dealname", "Deal Name"),
    ("amount", "Amount"),
    ("dealstage", "Stage"),
    ("pipeline", "Pipeline"),
    ("closedate", "Close Date"),
]

DEAL_DETAIL_COLUMNS = [
    ("id", "ID"),
    ("dealname", "Deal Name"),
    ("amount", "Amount"),
    ("dealstage", "Stage"),
    ("pipeline", "Pipeline"),
    ("closedate", "Close Date"),
    ("owner", "Owner ID"),
]


@click.group()
def deal() -> None:
    """Deal management commands."""
    pass


@deal.command("list")
@click.option("--limit", "-l", default=20, help="Number of results (max 100)")
@click.option("--after", help="Pagination cursor")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@click.option(
    "--filter",
    "-F",
    "filters",
    multiple=True,
    help="Filter by property (e.g. -F dealstage=closedwon). Operators: = != < > <= >= ~",
)
@pass_context
def list_deals(
    ctx: Context,
    limit: int,
    after: str | None,
    property: tuple[str, ...],
    filters: tuple[str, ...],
) -> None:
    """List deals."""
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        hubspot_filters = parse_filters(filters)
        filter_props = [f["propertyName"] for f in hubspot_filters or []]
        all_props = list(dict.fromkeys((props or []) + filter_props))
        if hubspot_filters:
            result = client.search_deals(
                filters=hubspot_filters,
                limit=limit,
                after=after,
                properties=all_props or None,
            )
        else:
            result = client.list_deals(
                limit=limit, after=after, properties=all_props or None
            )
    except Exception as e:
        print_error(f"Failed to list deals: {e}")
        return

    deals = result.get("results", [])
    extra = list(dict.fromkeys(list(property) + filter_props))
    data = [_format_deal(d, extra_properties=extra) for d in deals]

    columns = list(DEAL_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(
        data,
        ctx.format,
        columns=columns,
        title="Deals",
        template="{dealname} ({dealstage}) - {amount} ({id})",
    )

    paging = result.get("paging", {})
    next_after = paging.get("next", {}).get("after")
    if next_after:
        print_info(f"More results available. Use --after {next_after}")


@deal.command("show")
@click.argument("deal_id")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def show_deal(ctx: Context, deal_id: str, property: tuple[str, ...]) -> None:
    """Show details of a deal."""
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        d = client.get_deal(deal_id, properties=props)
    except Exception as e:
        print_error(f"Failed to get deal: {e}")
        return

    extra = list(property)
    data = _format_deal(d, extra_properties=extra)

    columns = list(DEAL_DETAIL_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(data, ctx.format, columns=columns)


@deal.command("search")
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Number of results (max 200)")
@click.option("--after", help="Pagination cursor")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@click.option(
    "--filter",
    "-F",
    "filters",
    multiple=True,
    help="Filter by property (e.g. -F dealstage=closedwon). Operators: = != < > <= >= ~",
)
@pass_context
def search_deals(
    ctx: Context,
    query: str,
    limit: int,
    after: str | None,
    property: tuple[str, ...],
    filters: tuple[str, ...],
) -> None:
    """Search deals by name, etc.

    QUERY is a free-text search across default searchable properties.
    """
    client = ctx.ensure_client()

    try:
        hubspot_filters = parse_filters(filters)
        filter_props = [f["propertyName"] for f in hubspot_filters or []]
        all_props = list(
            dict.fromkeys((list(property) if property else []) + filter_props)
        )
        result = client.search_deals(
            query=query,
            filters=hubspot_filters,
            limit=limit,
            after=after,
            properties=all_props or None,
        )
    except Exception as e:
        print_error(f"Search failed: {e}")
        return

    deals = result.get("results", [])
    extra = list(dict.fromkeys(list(property) + filter_props))
    data = [_format_deal(d, extra_properties=extra) for d in deals]

    columns = list(DEAL_COLUMNS)
    for name in extra:
        if not any(col[0] == name for col in columns):
            columns.append((name, name))

    format_output(
        data,
        ctx.format,
        columns=columns,
        title=f"Search: {query}",
        template="{dealname} ({dealstage}) - {amount} ({id})",
    )

    total = result.get("total", len(deals))
    paging = result.get("paging", {})
    next_after = paging.get("next", {}).get("after")
    if next_after:
        print_info(f"Showing {len(deals)} of {total}. Use --after {next_after}")


@deal.command("create")
@click.option("--name", "-n", required=True, help="Deal name")
@click.option("--stage", "-s", required=True, help="Deal stage ID")
@click.option("--pipeline", help="Pipeline ID (uses default if omitted)")
@click.option("--amount", "-a", help="Deal amount")
@click.option("--closedate", help="Expected close date (YYYY-MM-DD)")
@click.option("--owner", help="Owner ID")
@click.option(
    "--prop",
    multiple=True,
    help="Additional property as key=value",
)
@pass_context
def create_deal(
    ctx: Context,
    name: str,
    stage: str,
    pipeline: str | None,
    amount: str | None,
    closedate: str | None,
    owner: str | None,
    prop: tuple[str, ...],
) -> None:
    """Create a new deal."""
    client = ctx.ensure_client()

    properties: dict[str, str] = {"dealname": name, "dealstage": stage}
    if pipeline:
        properties["pipeline"] = pipeline
    if amount:
        properties["amount"] = amount
    if closedate:
        properties["closedate"] = closedate
    if owner:
        properties["hubspot_owner_id"] = owner
    for p in prop:
        key, _, value = p.partition("=")
        if not value:
            print_error(f"Invalid property format: {p} (expected key=value)")
            return
        properties[key] = value

    try:
        d = client.create_deal(properties)
        print_success(f"Created deal: {d['id']}")
    except Exception as e:
        print_error(f"Failed to create deal: {e}")


@deal.command("update")
@click.argument("deal_id")
@click.option("--name", "-n", help="Deal name")
@click.option("--stage", "-s", help="Deal stage ID")
@click.option("--pipeline", help="Pipeline ID")
@click.option("--amount", "-a", help="Deal amount")
@click.option("--closedate", help="Expected close date (YYYY-MM-DD)")
@click.option("--owner", help="Owner ID")
@click.option(
    "--prop",
    multiple=True,
    help="Additional property as key=value",
)
@pass_context
def update_deal(
    ctx: Context,
    deal_id: str,
    name: str | None,
    stage: str | None,
    pipeline: str | None,
    amount: str | None,
    closedate: str | None,
    owner: str | None,
    prop: tuple[str, ...],
) -> None:
    """Update a deal's properties."""
    client = ctx.ensure_client()

    properties: dict[str, str] = {}
    if name:
        properties["dealname"] = name
    if stage:
        properties["dealstage"] = stage
    if pipeline:
        properties["pipeline"] = pipeline
    if amount:
        properties["amount"] = amount
    if closedate:
        properties["closedate"] = closedate
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
        client.update_deal(deal_id, properties)
        print_success(f"Updated deal: {deal_id}")
    except Exception as e:
        print_error(f"Failed to update deal: {e}")


@deal.command("delete")
@click.argument("deal_id")
@click.confirmation_option(prompt="Are you sure you want to delete this deal?")
@pass_context
def delete_deal(ctx: Context, deal_id: str) -> None:
    """Delete (archive) a deal."""
    client = ctx.ensure_client()

    try:
        client.delete_deal(deal_id)
        print_success(f"Deleted deal: {deal_id}")
    except Exception as e:
        print_error(f"Failed to delete deal: {e}")


@deal.command("merge")
@click.argument("primary_id")
@click.argument("merge_id")
@click.confirmation_option(
    prompt="Merge these deals? The second will be merged into the first and archived."
)
@pass_context
def merge_deals(ctx: Context, primary_id: str, merge_id: str) -> None:
    """Merge two deals into one.

    PRIMARY_ID is the deal to keep; MERGE_ID is merged into it and then
    archived. Both must be numeric record IDs.
    """
    client = ctx.ensure_client()
    merge_records(client, "deals", primary_id, merge_id)


@deal.command("stages")
@click.option("--pipeline", "-p", help="Pipeline ID (lists all pipelines if omitted)")
@pass_context
def deal_stages(ctx: Context, pipeline: str | None) -> None:
    """List deal pipelines and stages."""
    client = ctx.ensure_client()

    try:
        pipelines = client.get_deal_pipelines()
    except Exception as e:
        print_error(f"Failed to get pipelines: {e}")
        return

    if pipeline:
        pipelines = [p for p in pipelines if p["id"] == pipeline]
        if not pipelines:
            print_error(f"Pipeline not found: {pipeline}")
            return

    data = []
    for p in pipelines:
        for stage in p.get("stages", []):
            data.append(
                {
                    "pipeline_id": p["id"],
                    "pipeline": p.get("label", p["id"]),
                    "stage_id": stage["id"],
                    "stage": stage.get("label", stage["id"]),
                    "display_order": stage.get("displayOrder", ""),
                }
            )

    format_output(
        data,
        ctx.format,
        columns=[
            ("pipeline", "Pipeline"),
            ("stage", "Stage"),
            ("stage_id", "Stage ID"),
            ("pipeline_id", "Pipeline ID"),
        ],
        title="Deal Stages",
        template="{pipeline} > {stage} ({stage_id})",
    )


@deal.command("owners")
@pass_context
def deal_owners(ctx: Context) -> None:
    """List available deal owners."""
    client = ctx.ensure_client()

    try:
        owners = client.list_owners()
    except Exception as e:
        print_error(f"Failed to list owners: {e}")
        return

    data = [
        {
            "id": o["id"],
            "email": o.get("email", ""),
            "firstname": o.get("firstName", ""),
            "lastname": o.get("lastName", ""),
        }
        for o in owners
    ]

    format_output(
        data,
        ctx.format,
        columns=[
            ("id", "ID"),
            ("firstname", "First Name"),
            ("lastname", "Last Name"),
            ("email", "Email"),
        ],
        title="Owners",
        template="{firstname} {lastname} <{email}> ({id})",
    )


@deal.command("associate")
@click.argument("deal_id")
@click.option(
    "--company",
    "-c",
    "companies",
    multiple=True,
    help="Company ID to associate (repeatable)",
)
@click.option(
    "--contact",
    "-C",
    "contacts",
    multiple=True,
    help="Contact ID to associate (repeatable)",
)
@click.option(
    "--label",
    "-L",
    "labels",
    multiple=True,
    help="Association label name or type ID (repeatable). See 'deal labels'.",
)
@pass_context
def associate_deal(
    ctx: Context,
    deal_id: str,
    companies: tuple[str, ...],
    contacts: tuple[str, ...],
    labels: tuple[str, ...],
) -> None:
    """Associate a deal with companies and/or contacts."""
    client = ctx.ensure_client()
    change_associations(
        client,
        "deals",
        deal_id,
        [("companies", companies), ("contacts", contacts)],
        remove=False,
        labels=labels,
    )


@deal.command("disassociate")
@click.argument("deal_id")
@click.option(
    "--company",
    "-c",
    "companies",
    multiple=True,
    help="Company ID to disassociate (repeatable)",
)
@click.option(
    "--contact",
    "-C",
    "contacts",
    multiple=True,
    help="Contact ID to disassociate (repeatable)",
)
@pass_context
def disassociate_deal(
    ctx: Context,
    deal_id: str,
    companies: tuple[str, ...],
    contacts: tuple[str, ...],
) -> None:
    """Remove associations between a deal and companies and/or contacts."""
    client = ctx.ensure_client()
    change_associations(
        client,
        "deals",
        deal_id,
        [("companies", companies), ("contacts", contacts)],
        remove=True,
    )


@deal.command("associations")
@click.argument("deal_id")
@pass_context
def deal_associations(ctx: Context, deal_id: str) -> None:
    """List companies and contacts associated with a deal."""
    client = ctx.ensure_client()
    show_associations(client, "deals", deal_id, ["companies", "contacts"], ctx.format)


@deal.command("labels")
@pass_context
def deal_labels(ctx: Context) -> None:
    """List association labels available from deals to companies and contacts."""
    client = ctx.ensure_client()
    show_labels(client, "deals", ["companies", "contacts"], ctx.format)


@deal.command("add-note")
@click.argument("deal_id")
@click.option("--body", "-b", required=True, help="Note text")
@pass_context
def add_note(ctx: Context, deal_id: str, body: str) -> None:
    """Add a note to a deal."""
    client = ctx.ensure_client()

    try:
        note = client.add_note("deals", deal_id, body)
        print_success(f"Added note {note['id']} to deal {deal_id}")
    except Exception as e:
        print_error(f"Failed to add note: {e}")


@deal.command("notes")
@click.argument("deal_id")
@pass_context
def list_notes(ctx: Context, deal_id: str) -> None:
    """List notes for a deal."""
    client = ctx.ensure_client()

    try:
        notes = client.list_notes("deals", deal_id)
    except Exception as e:
        print_error(f"Failed to list notes: {e}")
        return

    data = format_notes(notes)
    format_output(
        data,
        ctx.format,
        columns=NOTE_COLUMNS,
        title=f"Notes for deal {deal_id}",
        template="{id}: {body}",
    )


@deal.command("delete-note")
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
