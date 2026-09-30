"""Shared property subcommands for contacts, companies, and deals.

HubSpot does not mark properties as required in their definitions. A missing
required property only shows up as a VALIDATION_ERROR when creating a record,
which the create commands report together with a pointer to 'property'.
"""

import click

from hubspotctl.cli import Context, pass_context
from hubspotctl.client import HubSpotAPIError
from hubspotctl.output import (
    OutputFormat,
    format_output,
    output_json,
    output_table,
    print_error,
    print_info,
)

# Singular labels used in human-facing messages.
SINGULAR = {
    "contacts": "contact",
    "companies": "company",
    "deals": "deal",
}

PROPERTY_COLUMNS = [
    ("name", "Name"),
    ("label", "Label"),
    ("type", "Type"),
    ("group", "Group"),
    ("custom", "Custom"),
]

PROPERTY_DETAIL_COLUMNS = [
    ("name", "Name"),
    ("label", "Label"),
    ("type", "Type"),
    ("field_type", "Field Type"),
    ("group", "Group"),
    ("custom", "Custom"),
    ("read_only", "Read-only"),
    ("description", "Description"),
]

OPTION_COLUMNS = [
    ("value", "Value"),
    ("label", "Label"),
]


def format_property(p: dict) -> dict:
    """Extract display fields from a property definition."""
    metadata = p.get("modificationMetadata") or {}
    return {
        "name": p.get("name") or "",
        "label": p.get("label") or "",
        "type": p.get("type") or "",
        "field_type": p.get("fieldType") or "",
        "group": p.get("groupName") or "",
        "custom": "no" if p.get("hubspotDefined") else "yes",
        "read_only": "yes" if metadata.get("readOnlyValue") else "no",
        "description": p.get("description") or "",
    }


def print_missing_properties_hint(error: Exception, singular: str) -> None:
    """Point to the 'property' command for each required property that was missing."""
    if not isinstance(error, HubSpotAPIError) or not error.missing_properties:
        return
    for name in error.missing_properties:
        print_info(
            f"'{name}' is required. See its allowed values with: "
            f"hubspotctl {singular} property {name}"
        )


def register_property_commands(group: click.Group, object_type: str) -> None:
    """Add the property subcommands to a contact, company, or deal group."""
    singular = SINGULAR[object_type]

    @group.command("properties", help=f"List the properties of {object_type}.")
    @click.option(
        "--search", "-s", help="Only show properties whose name or label contains this"
    )
    @click.option("--custom", is_flag=True, help="Only show custom properties")
    @click.option("--hidden", is_flag=True, help="Include hidden properties")
    @pass_context
    def list_properties(
        ctx: Context, search: str | None, custom: bool, hidden: bool
    ) -> None:
        client = ctx.ensure_client()

        try:
            properties = client.list_properties(object_type)
        except Exception as e:
            print_error(f"Failed to list properties: {e}")
            return

        if not hidden:
            properties = [p for p in properties if not p.get("hidden")]
        if custom:
            properties = [p for p in properties if not p.get("hubspotDefined")]
        if search:
            needle = search.lower()
            properties = [
                p
                for p in properties
                if needle in (p.get("name") or "").lower()
                or needle in (p.get("label") or "").lower()
            ]

        data = sorted((format_property(p) for p in properties), key=lambda p: p["name"])
        format_output(
            data,
            ctx.format,
            columns=PROPERTY_COLUMNS,
            title=f"Properties of {object_type}",
            template="{name}: {label} ({type})",
        )

    @group.command(
        "property",
        help=f"Show a {singular} property, including its allowed values.",
    )
    @click.argument("name")
    @pass_context
    def show_property(ctx: Context, name: str) -> None:
        client = ctx.ensure_client()

        try:
            p = client.get_property(object_type, name)
        except Exception as e:
            print_error(f"Failed to get property: {e}")
            return

        options = [
            {"value": o.get("value") or "", "label": o.get("label") or ""}
            for o in p.get("options") or []
            if not o.get("hidden")
        ]

        if ctx.format == OutputFormat.JSON:
            output_json({**format_property(p), "options": options})
            return

        details = format_property(p)
        if ctx.format == OutputFormat.TABLE:
            # One row per field, since the description is too long for a column
            output_table(
                [
                    {"field": header, "value": details[key]}
                    for key, header in PROPERTY_DETAIL_COLUMNS
                ],
                columns=[("field", "Field"), ("value", "Value")],
            )
        else:
            format_output(
                details,
                ctx.format,
                columns=PROPERTY_DETAIL_COLUMNS,
                template="{name}: {label} ({type})\n{description}",
            )
        if options:
            format_output(
                options,
                ctx.format,
                columns=OPTION_COLUMNS,
                title="Allowed values",
                template="{value}",
            )
