# hubspotctl

[![PyPI version](https://img.shields.io/pypi/v/hubspotctl.svg)](https://pypi.org/project/hubspotctl)
[![Python package](https://github.com/slhck/hubspotctl/actions/workflows/python-package.yml/badge.svg)](https://github.com/slhck/hubspotctl/actions/workflows/python-package.yml)

A command-line interface for HubSpot CRM, written in Python.

## Requirements

- Python 3.11+

## Installation

Simply run it via [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uvx hubspotctl
```

Or install via [pipx](https://pipx.pypa.io/latest/installation/).
Or manually via pip:

```bash
pip install hubspotctl
```

## Usage

### Authentication

Before using the CLI, you need to authenticate with HubSpot:

1. Go to your HubSpot account settings
2. Navigate to Integrations > Private Apps (or Development > Legacy apps > Create legacy app > Private)
3. Create a private app with the following scopes:
   - `crm.objects.contacts.read`, `crm.objects.contacts.write`
   - `crm.objects.contacts.sensitive.read`, `crm.objects.contacts.highly_sensitive.read`
   - `crm.objects.companies.read`, `crm.objects.companies.write`
   - `crm.objects.companies.sensitive.read`, `crm.objects.companies.highly_sensitive.read`
   - `crm.objects.deals.read`, `crm.objects.deals.write`
   - `crm.objects.deals.sensitive.read`, `crm.objects.deals.highly_sensitive.read`
   - `crm.schemas.contacts.read`, `crm.schemas.contacts.write`
   - `crm.schemas.companies.read`, `crm.schemas.companies.write`
   - `crm.schemas.deals.read`, `crm.schemas.deals.write`
4. Copy your access token and run:

```bash
hubspotctl auth login
```

Credentials are stored securely in your system keychain.

To check your authentication status:

```bash
hubspotctl auth status
```

To remove stored credentials:

```bash
hubspotctl auth logout
```

### Basic Command Examples

```bash
# List contacts
hubspotctl contact list

# Search contacts
hubspotctl contact search "john"

# Show a contact by ID or email
hubspotctl contact show 12345
hubspotctl contact show john@example.com

# Create a contact
hubspotctl contact create --email john@example.com --firstname John --lastname Doe

# List companies
hubspotctl company list

# Search companies
hubspotctl company search "acme"

# Create a company
hubspotctl company create --name "Acme Inc" --domain acme.com --industry Technology

# List deals
hubspotctl deal list

# Search deals
hubspotctl deal search "enterprise"

# Show deal stages and owners
hubspotctl deal stages
hubspotctl deal owners

# Output as JSON
hubspotctl --format json contact list

# Output as CSV
hubspotctl --format csv deal list
```

## Command Reference

### Global Options

| Option | Description |
|--------|-------------|
| `--format`, `-f` | Output format: `table` (default), `json`, `csv`, `plain` |
| `--profile`, `-p` | Configuration profile to use (default: `default`) |
| `--version` | Show version and exit |
| `--help` | Show help and exit |

### `hubspotctl auth`

Authentication commands.

| Command | Description |
|---------|-------------|
| `auth login [--token]` | Set up authentication with HubSpot |
| `auth status` | Check authentication status |
| `auth logout` | Remove stored credentials |

### `hubspotctl contact`

Contact management commands.

| Command | Description |
|---------|-------------|
| `contact list [--limit] [--after] [--property]` | List contacts |
| `contact show <contact_id> [--property]` | Show details of a contact (ID or email) |
| `contact search <query> [--limit] [--after] [--property]` | Search contacts by name, email, etc. |
| `contact create --email <email> [--firstname] [--lastname] [--phone] [--company] [--jobtitle] [--prop key=value]` | Create a new contact |
| `contact update <contact_id> [--email] [--firstname] [--lastname] [--phone] [--company] [--jobtitle] [--prop key=value]` | Update a contact |
| `contact delete <contact_id>` | Delete (archive) a contact |

### `hubspotctl company`

Company management commands.

| Command | Description |
|---------|-------------|
| `company list [--limit] [--after] [--property]` | List companies |
| `company show <company_id> [--property]` | Show details of a company |
| `company search <query> [--limit] [--after] [--property]` | Search companies by name, domain, etc. |
| `company create --name <name> [--domain] [--industry] [--phone] [--owner] [--prop key=value]` | Create a new company |
| `company update <company_id> [--name] [--domain] [--industry] [--phone] [--owner] [--prop key=value]` | Update a company |
| `company delete <company_id>` | Delete (archive) a company |

### `hubspotctl deal`

Deal management commands.

| Command | Description |
|---------|-------------|
| `deal list [--limit] [--after] [--property]` | List deals |
| `deal show <deal_id> [--property]` | Show details of a deal |
| `deal search <query> [--limit] [--after] [--property]` | Search deals by name, etc. |
| `deal create --name <name> --stage <stage> [--pipeline] [--amount] [--closedate] [--owner] [--prop key=value]` | Create a new deal |
| `deal update <deal_id> [--name] [--stage] [--pipeline] [--amount] [--closedate] [--owner] [--prop key=value]` | Update a deal |
| `deal delete <deal_id>` | Delete (archive) a deal |
| `deal stages [--pipeline]` | List deal pipelines and stages |
| `deal owners` | List available deal owners |

### Multiple Profiles

You can use multiple HubSpot accounts by specifying a profile:

```bash
# Set up a work profile
HUBSPOTCTL_PROFILE=work hubspotctl auth login

# Use the work profile
hubspotctl --profile work contact list
```

## License

MIT License

Copyright (c) 2025 Werner Robitza

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
