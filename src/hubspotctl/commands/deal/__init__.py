"""Deal commands."""

import click

from hubspotctl.cli import Context, pass_context
from hubspotctl.output import format_output, print_error, print_success, print_info


def _format_deal(d: dict) -> dict:
    """Extract display fields from a deal API response."""
    props = d.get("properties", {})
    return {
        "id": d["id"],
        "dealname": props.get("dealname") or "",
        "amount": props.get("amount") or "",
        "dealstage": props.get("dealstage") or "",
        "pipeline": props.get("pipeline") or "",
        "closedate": props.get("closedate") or "",
        "owner": props.get("hubspot_owner_id") or "",
    }


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
@pass_context
def list_deals(
    ctx: Context, limit: int, after: str | None, property: tuple[str, ...]
) -> None:
    """List deals."""
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        result = client.list_deals(limit=limit, after=after, properties=props)
    except Exception as e:
        print_error(f"Failed to list deals: {e}")
        return

    deals = result.get("results", [])
    data = [_format_deal(d) for d in deals]

    format_output(
        data,
        ctx.format,
        columns=DEAL_COLUMNS,
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

    data = _format_deal(d)
    format_output(data, ctx.format, columns=DEAL_DETAIL_COLUMNS)


@deal.command("search")
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Number of results (max 200)")
@click.option("--after", help="Pagination cursor")
@click.option("--property", "-P", multiple=True, help="Additional properties to fetch")
@pass_context
def search_deals(
    ctx: Context,
    query: str,
    limit: int,
    after: str | None,
    property: tuple[str, ...],
) -> None:
    """Search deals by name, etc.

    QUERY is a free-text search across default searchable properties.
    """
    client = ctx.ensure_client()

    try:
        props = list(property) if property else None
        result = client.search_deals(
            query=query, limit=limit, after=after, properties=props
        )
    except Exception as e:
        print_error(f"Search failed: {e}")
        return

    deals = result.get("results", [])
    data = [_format_deal(d) for d in deals]

    format_output(
        data,
        ctx.format,
        columns=DEAL_COLUMNS,
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
