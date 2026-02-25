"""Shared test fixtures."""

from __future__ import annotations

from typing import Any

import pytest

from hubspotctl.client import HubSpotClient


@pytest.fixture
def mock_contacts() -> list[dict[str, Any]]:
    """Sample contact data from HubSpot API."""
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
    """Sample deal data from HubSpot API."""
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
def mock_pipelines() -> list[dict[str, Any]]:
    """Sample pipeline data."""
    return [
        {
            "id": "default",
            "label": "Sales Pipeline",
            "stages": [
                {
                    "id": "appointmentscheduled",
                    "label": "Appointment Scheduled",
                    "displayOrder": 0,
                },
                {
                    "id": "qualifiedtobuy",
                    "label": "Qualified To Buy",
                    "displayOrder": 1,
                },
                {"id": "contractsent", "label": "Contract Sent", "displayOrder": 2},
                {"id": "closedwon", "label": "Closed Won", "displayOrder": 3},
                {"id": "closedlost", "label": "Closed Lost", "displayOrder": 4},
            ],
        }
    ]


@pytest.fixture
def mock_owners() -> list[dict[str, Any]]:
    """Sample owner data."""
    return [
        {
            "id": "12345",
            "email": "owner@example.com",
            "firstName": "Sales",
            "lastName": "Rep",
        },
    ]


@pytest.fixture
def mock_client(mocker: Any) -> HubSpotClient:
    """Create a mock HubSpot client."""
    client = HubSpotClient(token="test_token")
    mocker.patch.object(client, "_client")
    return client
