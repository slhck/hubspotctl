"""Tests for the HubSpot API client."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest

from hubspotctl.client import HubSpotClient


class TestHubSpotClient:
    """Tests for HubSpotClient."""

    def test_auth_header(self) -> None:
        """Test that auth header is set correctly."""
        client = HubSpotClient(token="my_token")
        assert client._client.headers["Authorization"] == "Bearer my_token"

    def test_list_contacts(self, mocker: Any, mock_contacts: list[dict]) -> None:
        """Test listing contacts."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": mock_contacts}

        mocker.patch.object(client._client, "request", return_value=mock_response)

        result = client.list_contacts()

        assert len(result["results"]) == 2
        assert result["results"][0]["properties"]["email"] == "john@example.com"

    def test_get_contact(self, mocker: Any, mock_contacts: list[dict]) -> None:
        """Test getting a single contact."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_contacts[0]

        mocker.patch.object(client._client, "request", return_value=mock_response)

        contact = client.get_contact("101")

        assert contact["properties"]["firstname"] == "John"

    def test_get_contact_by_email(self, mocker: Any, mock_contacts: list[dict]) -> None:
        """Test getting a contact by email."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_contacts[0]

        mock_request = mocker.patch.object(
            client._client, "request", return_value=mock_response
        )

        client.get_contact_by_email("john@example.com")

        call_kwargs = mock_request.call_args
        assert "idProperty" in str(call_kwargs)

    def test_create_contact(self, mocker: Any) -> None:
        """Test creating a contact."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "103",
            "properties": {"email": "new@example.com", "firstname": "New"},
        }

        mocker.patch.object(client._client, "request", return_value=mock_response)

        contact = client.create_contact({"email": "new@example.com", "firstname": "New"})

        assert contact["id"] == "103"

    def test_update_contact(self, mocker: Any) -> None:
        """Test updating a contact."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "101",
            "properties": {"firstname": "Updated"},
        }

        mocker.patch.object(client._client, "request", return_value=mock_response)

        contact = client.update_contact("101", {"firstname": "Updated"})

        assert contact["properties"]["firstname"] == "Updated"

    def test_delete_contact(self, mocker: Any) -> None:
        """Test deleting a contact."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_request = mocker.patch.object(
            client._client, "request", return_value=mock_response
        )

        client.delete_contact("101")

        mock_request.assert_called_once()

    def test_search_contacts(self, mocker: Any, mock_contacts: list[dict]) -> None:
        """Test searching contacts."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": mock_contacts, "total": 2}

        mocker.patch.object(client._client, "request", return_value=mock_response)

        result = client.search_contacts(query="john")

        assert result["total"] == 2

    def test_list_deals(self, mocker: Any, mock_deals: list[dict]) -> None:
        """Test listing deals."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": mock_deals}

        mocker.patch.object(client._client, "request", return_value=mock_response)

        result = client.list_deals()

        assert len(result["results"]) == 2
        assert result["results"][0]["properties"]["dealname"] == "Enterprise License"

    def test_get_deal(self, mocker: Any, mock_deals: list[dict]) -> None:
        """Test getting a single deal."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_deals[0]

        mocker.patch.object(client._client, "request", return_value=mock_response)

        deal = client.get_deal("201")

        assert deal["properties"]["dealname"] == "Enterprise License"

    def test_create_deal(self, mocker: Any) -> None:
        """Test creating a deal."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "203",
            "properties": {"dealname": "New Deal", "dealstage": "qualifiedtobuy"},
        }

        mocker.patch.object(client._client, "request", return_value=mock_response)

        deal = client.create_deal({"dealname": "New Deal", "dealstage": "qualifiedtobuy"})

        assert deal["id"] == "203"

    def test_update_deal(self, mocker: Any) -> None:
        """Test updating a deal."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "201",
            "properties": {"amount": "75000"},
        }

        mocker.patch.object(client._client, "request", return_value=mock_response)

        deal = client.update_deal("201", {"amount": "75000"})

        assert deal["properties"]["amount"] == "75000"

    def test_delete_deal(self, mocker: Any) -> None:
        """Test deleting a deal."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_request = mocker.patch.object(
            client._client, "request", return_value=mock_response
        )

        client.delete_deal("201")

        mock_request.assert_called_once()

    def test_search_deals(self, mocker: Any, mock_deals: list[dict]) -> None:
        """Test searching deals."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": mock_deals, "total": 2}

        mocker.patch.object(client._client, "request", return_value=mock_response)

        result = client.search_deals(query="enterprise")

        assert result["total"] == 2

    def test_get_deal_pipelines(self, mocker: Any, mock_pipelines: list[dict]) -> None:
        """Test getting deal pipelines."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": mock_pipelines}

        mocker.patch.object(client._client, "request", return_value=mock_response)

        pipelines = client.get_deal_pipelines()

        assert len(pipelines) == 1
        assert pipelines[0]["label"] == "Sales Pipeline"

    def test_list_owners(self, mocker: Any, mock_owners: list[dict]) -> None:
        """Test listing owners."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": mock_owners}

        mocker.patch.object(client._client, "request", return_value=mock_response)

        owners = client.list_owners()

        assert len(owners) == 1
        assert owners[0]["email"] == "owner@example.com"

    def test_request_raises_on_error(self, mocker: Any) -> None:
        """Test that HTTP errors are raised."""
        client = HubSpotClient(token="test_token")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )

        mocker.patch.object(client._client, "request", return_value=mock_response)

        with pytest.raises(httpx.HTTPStatusError):
            client.list_contacts()
