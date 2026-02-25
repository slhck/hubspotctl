# hubspotctl

CLI for HubSpot CRM (contacts, companies, deals). Built with Click, httpx, keyring, Rich.

## Development

```bash
uv sync                                    # Install dependencies
uv run hubspotctl                          # Run CLI
uv run pytest                              # Run all tests
uv run ruff check src tests                # Lint
uv run mypy src                            # Type checking
```

## Architecture

Layered: CLI (Click) -> Context -> Client (httpx) / Config (keyring) / Output (Rich).

Commands live in `src/hubspotctl/commands/{auth,company,contact,deal}/`.

HubSpot CRM API v3 base URL: `https://api.hubapi.com`. Auth via Bearer token (private app access token).
