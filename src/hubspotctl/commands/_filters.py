"""Filter parsing utilities for HubSpot search API."""

import click

OPERATORS = {
    "!=": "NEQ",
    "<=": "LTE",
    ">=": "GTE",
    "<": "LT",
    ">": "GT",
    "~": "CONTAINS_TOKEN",
    "=": "EQ",
}


def parse_filters(filter_strings: tuple[str, ...]) -> list[dict] | None:
    """Parse filter strings like 'prop=value' or 'prop!=value' into HubSpot filters.

    Supported operators: = != < > <= >= ~ (CONTAINS_TOKEN)
    """
    if not filter_strings:
        return None

    filters = []
    for f in filter_strings:
        parsed = False
        for op_str, op_name in OPERATORS.items():
            idx = f.find(op_str)
            if idx > 0:
                prop = f[:idx]
                value = f[idx + len(op_str) :]
                filters.append(
                    {
                        "propertyName": prop,
                        "operator": op_name,
                        "value": value,
                    }
                )
                parsed = True
                break
        if not parsed:
            raise click.UsageError(
                f"Invalid filter format: {f} (expected property=value)"
            )
    return filters
