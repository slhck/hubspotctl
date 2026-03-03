"""Shared helpers for note subcommands."""


def _format_note(n: dict) -> dict:
    """Extract display fields from a note API response."""
    props = n.get("properties", {})
    body = props.get("hs_note_body") or ""
    # Strip HTML tags for plain-text display
    import re

    body = re.sub(r"<[^>]+>", "", body)
    return {
        "id": n["id"],
        "body": body,
        "timestamp": props.get("hs_timestamp") or "",
    }


def format_notes(notes: list[dict]) -> list[dict]:
    """Format a list of note API responses."""
    return [_format_note(n) for n in notes]


NOTE_COLUMNS = [
    ("id", "ID"),
    ("timestamp", "Timestamp"),
    ("body", "Body"),
]
