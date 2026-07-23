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

Before using the CLI, you need to authenticate with HubSpot by creating a Service Key (recommended) or a legacy private app.

**Service Keys** (recommended): Go to Settings > Integrations > Service Keys (or Development > Keys > Service Keys) and create a key with the scopes listed below.

**Legacy private apps**: Go to Settings > Integrations > Private Apps and create a private app with the scopes listed below. Note that HubSpot recommends Service Keys for new integrations.

Required scopes:

- `crm.objects.contacts.read`, `crm.objects.contacts.write`
- `crm.objects.contacts.sensitive.read`, `crm.objects.contacts.highly_sensitive.read`
- `crm.objects.companies.read`, `crm.objects.companies.write`
- `crm.objects.companies.sensitive.read`, `crm.objects.companies.highly_sensitive.read`
- `crm.objects.deals.read`, `crm.objects.deals.write`
- `crm.objects.deals.sensitive.read`, `crm.objects.deals.highly_sensitive.read`
- `crm.objects.owners.read`
- `crm.schemas.contacts.read`, `crm.schemas.contacts.write`
- `crm.schemas.companies.read`, `crm.schemas.companies.write`
- `crm.schemas.deals.read`, `crm.schemas.deals.write`

Copy your access token and run:

```bash
hubspotctl auth login
```

Credentials are stored securely in your system keychain.

Alternatively, provide the token through the environment:

```bash
HUBSPOT_ACCESS_TOKEN=your-token hubspotctl contact list
```

`HUBSPOT_ACCESS_TOKEN` takes precedence over tokens stored in the system
keychain. It applies regardless of the selected profile.

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

# Associate a deal with a company and contacts
hubspotctl deal associate 201 --company 301 --contact 101 --contact 102

# List a deal's associated companies and contacts
hubspotctl deal associations 201

# Merge a duplicate contact into another (the second is archived)
hubspotctl contact merge 101 102

# Add a note to a contact
hubspotctl contact add-note 12345 --body "Discussed pricing on call"

# List notes for a company
hubspotctl company notes 67890

# Filter by property value
hubspotctl contact list -F last_touchpoint="MWC 2026"

# Multiple filters (AND logic)
hubspotctl contact list -F last_touchpoint="MWC 2026" -F company=AVEQ

# Filter with comparison operators
hubspotctl deal list -F amount>=1000

# Combine search with filters
hubspotctl contact search "John" -F lifecyclestage=lead

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
| `contact list [--limit] [--after] [--property] [--filter]` | List contacts |
| `contact show <contact_id> [--property]` | Show details of a contact (ID or email) |
| `contact search <query> [--limit] [--after] [--property] [--filter]` | Search contacts by name, email, etc. |
| `contact create --email <email> [--firstname] [--lastname] [--phone] [--company] [--jobtitle] [--prop key=value]` | Create a new contact |
| `contact update <contact_id> [--email] [--firstname] [--lastname] [--phone] [--company] [--jobtitle] [--prop key=value]` | Update a contact |
| `contact delete <contact_id>` | Delete (archive) a contact |
| `contact merge <primary_id> <merge_id>` | Merge two contacts into one |
| `contact associate <contact_id> [--company <id>] [--deal <id>] [--label <name>]` | Associate a contact with companies and/or deals |
| `contact disassociate <contact_id> [--company <id>] [--deal <id>]` | Remove a contact's associations to companies and/or deals |
| `contact associations <contact_id>` | List companies and deals associated with a contact |
| `contact labels` | List association labels available from contacts |
| `contact add-note <contact_id> --body <text>` | Add a note to a contact |
| `contact notes <contact_id>` | List notes for a contact |
| `contact delete-note <note_id>` | Delete a note |

### `hubspotctl company`

Company management commands.

| Command | Description |
|---------|-------------|
| `company list [--limit] [--after] [--property] [--filter]` | List companies |
| `company show <company_id> [--property]` | Show details of a company |
| `company search <query> [--limit] [--after] [--property] [--filter]` | Search companies by name, domain, etc. |
| `company create --name <name> [--domain] [--industry] [--phone] [--owner] [--prop key=value]` | Create a new company |
| `company update <company_id> [--name] [--domain] [--industry] [--phone] [--owner] [--prop key=value]` | Update a company |
| `company delete <company_id>` | Delete (archive) a company |
| `company merge <primary_id> <merge_id>` | Merge two companies into one |
| `company associate <company_id> [--contact <id>] [--deal <id>] [--label <name>]` | Associate a company with contacts and/or deals |
| `company disassociate <company_id> [--contact <id>] [--deal <id>]` | Remove a company's associations to contacts and/or deals |
| `company associations <company_id>` | List contacts and deals associated with a company |
| `company labels` | List association labels available from companies |
| `company add-note <company_id> --body <text>` | Add a note to a company |
| `company notes <company_id>` | List notes for a company |
| `company delete-note <note_id>` | Delete a note |

### `hubspotctl deal`

Deal management commands.

| Command | Description |
|---------|-------------|
| `deal list [--limit] [--after] [--property] [--filter]` | List deals |
| `deal show <deal_id> [--property]` | Show details of a deal |
| `deal search <query> [--limit] [--after] [--property] [--filter]` | Search deals by name, etc. |
| `deal create --name <name> --stage <stage> [--pipeline] [--amount] [--closedate] [--owner] [--prop key=value]` | Create a new deal |
| `deal update <deal_id> [--name] [--stage] [--pipeline] [--amount] [--closedate] [--owner] [--prop key=value]` | Update a deal |
| `deal delete <deal_id>` | Delete (archive) a deal |
| `deal merge <primary_id> <merge_id>` | Merge two deals into one |
| `deal stages [--pipeline]` | List deal pipelines and stages |
| `deal owners` | List available deal owners |
| `deal associate <deal_id> [--company <id>] [--contact <id>] [--label <name>]` | Associate a deal with companies and/or contacts |
| `deal disassociate <deal_id> [--company <id>] [--contact <id>]` | Remove a deal's associations to companies and/or contacts |
| `deal associations <deal_id>` | List companies and contacts associated with a deal |
| `deal labels` | List association labels available from deals |
| `deal add-note <deal_id> --body <text>` | Add a note to a deal |
| `deal notes <deal_id>` | List notes for a deal |
| `deal delete-note <note_id>` | Delete a note |

### Associations

Records can be linked to each other: a deal to its company and contacts, a contact to companies and deals, and so on. The `associate`, `disassociate`, and `associations` commands manage these links. Each `--company`, `--contact`, or `--deal` option takes a record ID and can be repeated to link several records at once.

```bash
# Link a deal to a company and two contacts
hubspotctl deal associate 201 --company 301 --contact 101 --contact 102

# List everything linked to a deal
hubspotctl deal associations 201

# Unlink a contact from the deal
hubspotctl deal disassociate 201 --contact 102
```

By default these create the unlabeled HubSpot association. To apply a labeled association (e.g. "Primary", "Decision maker"), pass `--label` / `-L` with the label name or its numeric type ID. Use the `labels` command to see what is available for each object pair.

```bash
# See which labels exist from deals to companies and contacts
hubspotctl deal labels

# Link a contact to a company using a label
hubspotctl contact associate 101 --company 301 --label "Decision maker"
```

These commands expect numeric record IDs, not email addresses. `disassociate` removes all associations between the two records (it does not target a single label).

### Merging records

Two records of the same type can be merged into one with the `merge` command. The first ID is the record to keep; the second is merged into it and then archived. The kept record inherits properties and associations from both, with the primary record winning any conflicts.

```bash
# Merge a duplicate contact (102) into the one you want to keep (101)
hubspotctl contact merge 101 102

# Works the same way for companies and deals
hubspotctl company merge 301 302
hubspotctl deal merge 201 202
```

This is destructive (the second record is archived), so it asks for confirmation first. Pass `--yes` to skip the prompt. These commands expect numeric record IDs, not email addresses. Note that for contacts the resulting record may be assigned a new ID, which is shown in the output.

### Properties

Each object type has a set of default properties that are fetched and displayed. You can request additional properties with the `--property` / `-P` flag on `list`, `show`, and `search` commands. You can also set arbitrary custom properties when creating or updating objects with `--prop key=value`.

You can filter results by property values using `--filter` / `-F` on `list` and `search` commands. Supported operators: `=`, `!=`, `<`, `>`, `<=`, `>=`, `~` (contains token). Multiple filters are combined with AND logic. Filter properties are automatically included in the output.

**Contact properties** (default):

- `email` — email address
- `firstname` — first name
- `lastname` — last name
- `phone` — phone number
- `company` — associated company name
- `jobtitle` — job title (shown in detail view only)
- `lifecyclestage` — lifecycle stage (shown in detail view only)

**Company properties** (default):

- `name` — company name
- `domain` — website domain
- `industry` — industry classification
- `phone` — phone number
- `city` — city
- `state` — state/region (shown in detail view only)
- `country` — country
- `hubspot_owner_id` — assigned owner (shown as `owner` in detail view)

**Deal properties** (default):

- `dealname` — deal name
- `amount` — deal amount
- `dealstage` — current stage (internal ID)
- `pipeline` — pipeline (internal ID)
- `closedate` — expected close date
- `hubspot_owner_id` — assigned owner (shown as `owner` in detail view)

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
