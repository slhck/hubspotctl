"""Shared helpers for association subcommands.

Associations link CRM records to each other (e.g. a deal to a company). All
helpers operate on the plural object-type names used by the HubSpot v4 API
(``deals``, ``companies``, ``contacts``).
"""

from hubspotctl.client import HubSpotClient
from hubspotctl.output import OutputFormat, format_output, print_error, print_success

# Singular labels used in human-facing messages and CLI option names.
SINGULAR = {
    "contacts": "contact",
    "companies": "company",
    "deals": "deal",
}

# Properties fetched to build a readable label for each associated record.
_DISPLAY_PROPERTIES = {
    "contacts": ["firstname", "lastname", "email"],
    "companies": ["name", "domain"],
    "deals": ["dealname", "amount"],
}


def _label(object_type: str, props: dict) -> str:
    """Build a readable one-line label from a record's properties."""
    if object_type == "contacts":
        name = " ".join(p for p in (props.get("firstname"), props.get("lastname")) if p)
        email = props.get("email") or ""
        if name and email:
            return f"{name} <{email}>"
        return name or email
    if object_type == "companies":
        return props.get("name") or props.get("domain") or ""
    if object_type == "deals":
        return props.get("dealname") or ""
    return ""


def _resolve_labels(
    client: HubSpotClient,
    from_type: str,
    to_type: str,
    labels: tuple[str, ...],
) -> list[dict] | None:
    """Resolve label names or type IDs to association-type dicts for the API.

    Returns the list of ``{"associationCategory", "associationTypeId"}`` dicts,
    or ``None`` if any label cannot be resolved (an error is printed).
    """
    available = client.get_association_labels(from_type, to_type)
    resolved = []
    for label in labels:
        match = None
        for entry in available:
            name = entry.get("label")
            if str(entry.get("typeId")) == label.strip() or (
                name and name.lower() == label.strip().lower()
            ):
                match = entry
                break
        if match is None:
            names = ", ".join(e["label"] for e in available if e.get("label"))
            print_error(
                f"Unknown label '{label}' for {SINGULAR[from_type]} -> "
                f"{SINGULAR[to_type]}. Available: {names or '(none)'}"
            )
            return None
        resolved.append(
            {
                "associationCategory": match["category"],
                "associationTypeId": match["typeId"],
            }
        )
    return resolved


def change_associations(
    client: HubSpotClient,
    from_type: str,
    from_id: str,
    targets: list[tuple[str, tuple[str, ...]]],
    *,
    remove: bool,
    labels: tuple[str, ...] = (),
) -> None:
    """Create or remove associations from one record to many targets.

    ``targets`` is a list of ``(to_type, ids)`` pairs. At least one ID across
    all targets must be given. When ``labels`` are given (only valid when
    creating), labeled associations are created instead of default ones.
    """
    if not any(ids for _, ids in targets):
        opts = " or ".join(f"--{SINGULAR[to_type]}" for to_type, _ in targets)
        print_error(f"Specify at least one {opts}")
        return

    verb = "Disassociated" if remove else "Associated"
    preposition = "from" if remove else "with"
    suffix = f" [{', '.join(labels)}]" if labels else ""
    try:
        for to_type, ids in targets:
            if not ids:
                continue
            association_types = None
            if labels:
                association_types = _resolve_labels(client, from_type, to_type, labels)
                if association_types is None:
                    return
            for to_id in ids:
                if remove:
                    client.disassociate(from_type, from_id, to_type, to_id)
                elif association_types:
                    client.associate(
                        from_type,
                        from_id,
                        to_type,
                        to_id,
                        association_types=association_types,
                    )
                else:
                    client.associate(from_type, from_id, to_type, to_id)
                print_success(
                    f"{verb} {SINGULAR[from_type]} {from_id} {preposition} "
                    f"{SINGULAR[to_type]} {to_id}{suffix}"
                )
    except Exception as e:
        failed = "disassociate" if remove else "associate"
        print_error(f"Failed to {failed}: {e}")


def show_associations(
    client: HubSpotClient,
    from_type: str,
    from_id: str,
    to_types: list[str],
    fmt: OutputFormat,
) -> None:
    """List records associated with a record, grouped by target type.

    Each row also shows the association's labels, if any (the implicit
    unlabeled association is left blank).
    """
    data = []
    try:
        for to_type in to_types:
            assocs = client.list_associations(from_type, from_id, to_type)
            labels_by_id = {}
            ids = []
            for r in assocs:
                rid = str(r["toObjectId"])
                ids.append(rid)
                names = [
                    t["label"] for t in r.get("associationTypes", []) if t.get("label")
                ]
                labels_by_id[rid] = ", ".join(names)
            objs = client.batch_read(to_type, ids, _DISPLAY_PROPERTIES[to_type])
            for o in objs:
                data.append(
                    {
                        "type": SINGULAR[to_type],
                        "id": o["id"],
                        "name": _label(to_type, o.get("properties", {})),
                        "labels": labels_by_id.get(str(o["id"]), ""),
                    }
                )
    except Exception as e:
        print_error(f"Failed to list associations: {e}")
        return

    format_output(
        data,
        fmt,
        columns=[
            ("type", "Type"),
            ("id", "ID"),
            ("name", "Name"),
            ("labels", "Labels"),
        ],
        title=f"Associations for {SINGULAR[from_type]} {from_id}",
        template="{type}: {name} ({id}) {labels}",
    )


def show_labels(
    client: HubSpotClient,
    from_type: str,
    to_types: list[str],
    fmt: OutputFormat,
) -> None:
    """List the association labels available from one object type to others."""
    data = []
    try:
        for to_type in to_types:
            for entry in client.get_association_labels(from_type, to_type):
                data.append(
                    {
                        "target": SINGULAR[to_type],
                        "label": entry.get("label") or "(unlabeled)",
                        "category": entry.get("category", ""),
                        "type_id": entry.get("typeId", ""),
                    }
                )
    except Exception as e:
        print_error(f"Failed to list labels: {e}")
        return

    format_output(
        data,
        fmt,
        columns=[
            ("target", "Target"),
            ("label", "Label"),
            ("category", "Category"),
            ("type_id", "Type ID"),
        ],
        title=f"Association labels for {SINGULAR[from_type]}",
        template="{target}: {label} ({category}/{type_id})",
    )
