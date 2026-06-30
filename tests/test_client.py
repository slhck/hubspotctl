"""Tests for the HubSpot API client."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest

from hubspotctl.client import HubSpotClient


@pytest.fixture
def client(mocker: Any) -> HubSpotClient:
    c = HubSpotClient(token="test_token")
    mocker.patch.object(c, "_client")
    return c


def _mock_response(
    client: HubSpotClient, status: int = 200, json: Any = None
) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = json
    client._client.request.return_value = resp  # type: ignore[attr-defined]
    return resp


class TestHubSpotClient:
    def test_auth_header(self) -> None:
        client = HubSpotClient(token="my_token")
        assert client._client.headers["Authorization"] == "Bearer my_token"

    def test_raises_on_http_error(self, client: HubSpotClient) -> None:
        resp = _mock_response(client, status=401)
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=resp
        )
        with pytest.raises(httpx.HTTPStatusError):
            client.list_contacts()

    def test_delete_returns_none(self, client: HubSpotClient) -> None:
        _mock_response(client, status=204)
        assert client.delete_contact("101") is None

    def test_get_contact_by_email_uses_id_property(self, client: HubSpotClient) -> None:
        _mock_response(client, json={"id": "101", "properties": {}})
        client.get_contact_by_email("john@example.com")
        call_kwargs = client._client.request.call_args  # type: ignore[attr-defined]
        assert "idProperty" in str(call_kwargs)

    def test_get_deal_pipelines_extracts_results(
        self, client: HubSpotClient, mock_pipelines: list[dict]
    ) -> None:
        _mock_response(client, json={"results": mock_pipelines})
        pipelines = client.get_deal_pipelines()
        assert pipelines[0]["label"] == "Sales Pipeline"

    def test_list_owners_extracts_results(
        self, client: HubSpotClient, mock_owners: list[dict]
    ) -> None:
        _mock_response(client, json={"results": mock_owners})
        owners = client.list_owners()
        assert owners[0]["email"] == "owner@example.com"

    @pytest.mark.parametrize(
        "method,args",
        [
            ("list_contacts", []),
            ("list_companies", []),
            ("list_deals", []),
            ("get_contact", ["1"]),
            ("get_company", ["1"]),
            ("get_deal", ["1"]),
            ("create_contact", [{"email": "a@b.com"}]),
            ("create_company", [{"name": "X"}]),
            ("create_deal", [{"dealname": "X"}]),
            ("update_contact", ["1", {"email": "a@b.com"}]),
            ("update_company", ["1", {"name": "X"}]),
            ("update_deal", ["1", {"amount": "1"}]),
            ("search_contacts", []),
            ("search_companies", []),
            ("search_deals", []),
            ("create_note", ["Hello"]),
        ],
    )
    def test_crud_methods_callable(
        self, client: HubSpotClient, method: str, args: list
    ) -> None:
        _mock_response(client, json={"results": [], "total": 0, "id": "1"})
        getattr(client, method)(*args)
        client._client.request.assert_called_once()  # type: ignore[attr-defined]

    def test_associate_note(self, client: HubSpotClient) -> None:
        _mock_response(client, status=200, json={})
        client.associate_note("10", "contacts", "101")
        call_args = client._client.request.call_args  # type: ignore[attr-defined]
        assert call_args[0][0] == "PUT"
        assert "/note/10/associations/default/contacts/101" in call_args[0][1]

    def test_list_notes(self, client: HubSpotClient) -> None:
        # First call returns association IDs, second call returns note details
        resp1 = MagicMock()
        resp1.status_code = 200
        resp1.json.return_value = {
            "results": [{"toObjectId": "10"}, {"toObjectId": "11"}]
        }
        resp2 = MagicMock()
        resp2.status_code = 200
        resp2.json.return_value = {
            "results": [
                {"id": "10", "properties": {"hs_note_body": "Note 1"}},
                {"id": "11", "properties": {"hs_note_body": "Note 2"}},
            ]
        }
        client._client.request.side_effect = [resp1, resp2]  # type: ignore[attr-defined]
        notes = client.list_notes("contacts", "101")
        assert len(notes) == 2

    def test_list_notes_empty(self, client: HubSpotClient) -> None:
        _mock_response(client, json={"results": []})
        notes = client.list_notes("contacts", "101")
        assert notes == []

    def test_delete_note(self, client: HubSpotClient) -> None:
        _mock_response(client, status=204)
        assert client.delete_note("10") is None

    def test_associate(self, client: HubSpotClient) -> None:
        _mock_response(client, status=200, json={})
        client.associate("deals", "201", "companies", "301")
        call_args = client._client.request.call_args  # type: ignore[attr-defined]
        assert call_args[0][0] == "PUT"
        assert "/deals/201/associations/default/companies/301" in call_args[0][1]

    def test_associate_with_labels(self, client: HubSpotClient) -> None:
        _mock_response(client, status=200, json={})
        types = [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}]
        client.associate("deals", "201", "companies", "301", association_types=types)
        call_args = client._client.request.call_args  # type: ignore[attr-defined]
        assert call_args[0][0] == "PUT"
        # Labeled associations use the non-default endpoint with a body.
        assert "/deals/201/associations/companies/301" in call_args[0][1]
        assert "/default/" not in call_args[0][1]
        assert call_args.kwargs["json"] == types

    def test_disassociate(self, client: HubSpotClient) -> None:
        _mock_response(client, status=204)
        client.disassociate("deals", "201", "contacts", "101")
        call_args = client._client.request.call_args  # type: ignore[attr-defined]
        assert call_args[0][0] == "DELETE"
        assert "/deals/201/associations/contacts/101" in call_args[0][1]

    def test_get_association_labels(self, client: HubSpotClient) -> None:
        _mock_response(
            client,
            json={
                "results": [{"category": "USER_DEFINED", "typeId": 36, "label": "X"}]
            },
        )
        labels = client.get_association_labels("deals", "companies")
        assert labels[0]["label"] == "X"
        call_args = client._client.request.call_args  # type: ignore[attr-defined]
        assert "/crm/v4/associations/deals/companies/labels" in call_args[0][1]

    def test_list_associations(self, client: HubSpotClient) -> None:
        _mock_response(client, json={"results": [{"toObjectId": "301"}]})
        result = client.list_associations("deals", "201", "companies")
        assert result[0]["toObjectId"] == "301"

    def test_batch_read(self, client: HubSpotClient) -> None:
        _mock_response(client, json={"results": [{"id": "301", "properties": {}}]})
        result = client.batch_read("companies", ["301"], ["name"])
        assert result[0]["id"] == "301"
        client._client.request.assert_called_once()  # type: ignore[attr-defined]

    def test_batch_read_empty(self, client: HubSpotClient) -> None:
        assert client.batch_read("companies", []) == []
        client._client.request.assert_not_called()  # type: ignore[attr-defined]

    def test_batch_read_chunks_over_100(self, client: HubSpotClient) -> None:
        _mock_response(client, json={"results": [{"id": "1"}]})
        ids = [str(i) for i in range(250)]
        client.batch_read("companies", ids)
        # 250 IDs -> three requests of 100, 100, 50
        assert client._client.request.call_count == 3  # type: ignore[attr-defined]
