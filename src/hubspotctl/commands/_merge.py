"""Shared helper for the merge subcommand.

Merging combines two records of the same type into one. The primary record is
kept; the secondary record is merged into it and then archived. Operates on the
plural object-type names used by the HubSpot v3 API (``contacts``,
``companies``, ``deals``).
"""

from hubspotctl.client import HubSpotClient
from hubspotctl.output import print_error, print_success

# Singular labels used in human-facing messages.
SINGULAR = {
    "contacts": "contact",
    "companies": "company",
    "deals": "deal",
}


def merge_records(
    client: HubSpotClient,
    object_type: str,
    primary_id: str,
    merge_id: str,
) -> None:
    """Merge one record into another and report the result.

    ``primary_id`` is kept; ``merge_id`` is merged into it and then archived.
    The resulting record's ID may differ from ``primary_id``.
    """
    singular = SINGULAR[object_type]
    try:
        result = client.merge(object_type, primary_id, merge_id)
    except Exception as e:
        print_error(f"Failed to merge {singular}s: {e}")
        return

    result_id = result.get("id", primary_id)
    print_success(
        f"Merged {singular} {merge_id} into {singular} {primary_id} "
        f"(resulting {singular}: {result_id})"
    )
