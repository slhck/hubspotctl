"""Shared test fixtures."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def cli(runner: CliRunner) -> Any:
    """Provide (runner, mock_client) with Config and HubSpotClient patched."""
    mock_client = MagicMock()
    mock_config = MagicMock()
    mock_config.get_token.return_value = "test_token"
    mock_config.is_configured.return_value = True

    with (
        patch("hubspotctl.cli.Config", return_value=mock_config),
        patch("hubspotctl.cli.HubSpotClient", return_value=mock_client),
    ):
        yield runner, mock_client, mock_config


@pytest.fixture
def mock_contacts() -> list[dict[str, Any]]:
    return [
        {
            "id": "101",
            "properties": {
                "email": "john@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "phone": "+1234567890",
                "company": "Acme Inc",
                "jobtitle": "Engineer",
                "lifecyclestage": "lead",
            },
        },
        {
            "id": "102",
            "properties": {
                "email": "jane@example.com",
                "firstname": "Jane",
                "lastname": "Smith",
                "phone": "+0987654321",
                "company": "Globex",
                "jobtitle": "Manager",
                "lifecyclestage": "customer",
            },
        },
    ]


@pytest.fixture
def mock_deals() -> list[dict[str, Any]]:
    return [
        {
            "id": "201",
            "properties": {
                "dealname": "Enterprise License",
                "amount": "50000",
                "dealstage": "contractsent",
                "pipeline": "default",
                "closedate": "2026-03-15T00:00:00.000Z",
                "hubspot_owner_id": "12345",
            },
        },
        {
            "id": "202",
            "properties": {
                "dealname": "Starter Plan",
                "amount": "5000",
                "dealstage": "qualifiedtobuy",
                "pipeline": "default",
                "closedate": "2026-04-01T00:00:00.000Z",
                "hubspot_owner_id": "12345",
            },
        },
    ]


@pytest.fixture
def mock_companies() -> list[dict[str, Any]]:
    return [
        {
            "id": "301",
            "properties": {
                "name": "Acme Inc",
                "domain": "acme.com",
                "industry": "Technology",
                "phone": "+1234567890",
                "city": "San Francisco",
                "state": "CA",
                "country": "US",
                "hubspot_owner_id": "12345",
            },
        },
        {
            "id": "302",
            "properties": {
                "name": "Globex Corp",
                "domain": "globex.com",
                "industry": "Manufacturing",
                "phone": "+0987654321",
                "city": "Springfield",
                "state": "IL",
                "country": "US",
                "hubspot_owner_id": "12345",
            },
        },
    ]


@pytest.fixture
def mock_pipelines() -> list[dict[str, Any]]:
    return [
        {
            "id": "default",
            "label": "Sales Pipeline",
            "stages": [
                {"id": "appointmentscheduled", "label": "Appointment Scheduled", "displayOrder": 0},
                {"id": "qualifiedtobuy", "label": "Qualified To Buy", "displayOrder": 1},
                {"id": "contractsent", "label": "Contract Sent", "displayOrder": 2},
                {"id": "closedwon", "label": "Closed Won", "displayOrder": 3},
                {"id": "closedlost", "label": "Closed Lost", "displayOrder": 4},
            ],
        }
    ]


@pytest.fixture
def mock_owners() -> list[dict[str, Any]]:
    return [
        {"id": "12345", "email": "owner@example.com", "firstName": "Sales", "lastName": "Rep"},
    ]
