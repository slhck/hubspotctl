"""HubSpot CRM API client."""

import time
from typing import Any

import httpx

BASE_URL = "https://api.hubapi.com"

DEFAULT_CONTACT_PROPERTIES = [
    "email",
    "firstname",
    "lastname",
    "phone",
    "company",
    "jobtitle",
    "lifecyclestage",
]

DEFAULT_DEAL_PROPERTIES = [
    "dealname",
    "amount",
    "dealstage",
    "pipeline",
    "closedate",
    "hubspot_owner_id",
]

DEFAULT_COMPANY_PROPERTIES = [
    "name",
    "domain",
    "industry",
    "phone",
    "city",
    "state",
    "country",
    "hubspot_owner_id",
]


class HubSpotClient:
    """HTTP client for HubSpot CRM API v3."""

    def __init__(self, token: str) -> None:
        self.token = token
        self._client = httpx.Client(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
    ) -> Any:
        """Make an authenticated request to HubSpot API."""
        url = f"{BASE_URL}{path}"
        response = self._client.request(method, url, params=params, json=json)
        response.raise_for_status()

        if response.status_code == 204:
            return None
        return response.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        """Make a GET request."""
        return self._request("GET", path, params=params)

    def post(
        self, path: str, params: dict | None = None, json: dict | None = None
    ) -> Any:
        """Make a POST request."""
        return self._request("POST", path, params=params, json=json)

    def patch(
        self, path: str, params: dict | None = None, json: dict | None = None
    ) -> Any:
        """Make a PATCH request."""
        return self._request("PATCH", path, params=params, json=json)

    def put(
        self, path: str, params: dict | None = None, json: dict | None = None
    ) -> Any:
        """Make a PUT request."""
        return self._request("PUT", path, params=params, json=json)

    def delete(self, path: str, params: dict | None = None) -> Any:
        """Make a DELETE request."""
        return self._request("DELETE", path, params=params)

    # Account
    def get_me(self) -> dict:
        """Get account info to verify token."""
        return self.get("/account-info/v3/details")

    # Contacts
    def list_contacts(
        self,
        limit: int = 20,
        after: str | None = None,
        properties: list[str] | None = None,
    ) -> dict:
        """List contacts with pagination."""
        props = list(dict.fromkeys(DEFAULT_CONTACT_PROPERTIES + (properties or [])))
        params: dict[str, Any] = {
            "limit": limit,
            "properties": ",".join(props),
        }
        if after:
            params["after"] = after
        return self.get("/crm/v3/objects/contacts", params=params)

    def get_contact(self, contact_id: str, properties: list[str] | None = None) -> dict:
        """Get a contact by ID or email."""
        props = list(dict.fromkeys(DEFAULT_CONTACT_PROPERTIES + (properties or [])))
        params = {"properties": ",".join(props)}
        return self.get(f"/crm/v3/objects/contacts/{contact_id}", params=params)

    def get_contact_by_email(
        self, email: str, properties: list[str] | None = None
    ) -> dict:
        """Get a contact by email address."""
        props = list(dict.fromkeys(DEFAULT_CONTACT_PROPERTIES + (properties or [])))
        params: dict[str, str] = {
            "properties": ",".join(props),
            "idProperty": "email",
        }
        return self.get(f"/crm/v3/objects/contacts/{email}", params=params)

    def create_contact(self, properties: dict[str, str]) -> dict:
        """Create a new contact."""
        return self.post("/crm/v3/objects/contacts", json={"properties": properties})

    def update_contact(self, contact_id: str, properties: dict[str, str]) -> dict:
        """Update a contact."""
        return self.patch(
            f"/crm/v3/objects/contacts/{contact_id}",
            json={"properties": properties},
        )

    def delete_contact(self, contact_id: str) -> None:
        """Delete (archive) a contact."""
        self.delete(f"/crm/v3/objects/contacts/{contact_id}")

    def search_contacts(
        self,
        query: str | None = None,
        filters: list[dict] | None = None,
        properties: list[str] | None = None,
        limit: int = 20,
        after: str | None = None,
    ) -> dict:
        """Search contacts."""
        props = list(dict.fromkeys(DEFAULT_CONTACT_PROPERTIES + (properties or [])))
        body: dict[str, Any] = {
            "properties": props,
            "limit": limit,
        }
        if query:
            body["query"] = query
        if filters:
            body["filterGroups"] = [{"filters": filters}]
        if after:
            body["after"] = after
        return self.post("/crm/v3/objects/contacts/search", json=body)

    # Deals
    def list_deals(
        self,
        limit: int = 20,
        after: str | None = None,
        properties: list[str] | None = None,
    ) -> dict:
        """List deals with pagination."""
        props = list(dict.fromkeys(DEFAULT_DEAL_PROPERTIES + (properties or [])))
        params: dict[str, Any] = {
            "limit": limit,
            "properties": ",".join(props),
        }
        if after:
            params["after"] = after
        return self.get("/crm/v3/objects/deals", params=params)

    def get_deal(self, deal_id: str, properties: list[str] | None = None) -> dict:
        """Get a deal by ID."""
        props = list(dict.fromkeys(DEFAULT_DEAL_PROPERTIES + (properties or [])))
        params = {"properties": ",".join(props)}
        return self.get(f"/crm/v3/objects/deals/{deal_id}", params=params)

    def create_deal(self, properties: dict[str, str]) -> dict:
        """Create a new deal."""
        return self.post("/crm/v3/objects/deals", json={"properties": properties})

    def update_deal(self, deal_id: str, properties: dict[str, str]) -> dict:
        """Update a deal."""
        return self.patch(
            f"/crm/v3/objects/deals/{deal_id}",
            json={"properties": properties},
        )

    def delete_deal(self, deal_id: str) -> None:
        """Delete (archive) a deal."""
        self.delete(f"/crm/v3/objects/deals/{deal_id}")

    def search_deals(
        self,
        query: str | None = None,
        filters: list[dict] | None = None,
        properties: list[str] | None = None,
        limit: int = 20,
        after: str | None = None,
    ) -> dict:
        """Search deals."""
        props = list(dict.fromkeys(DEFAULT_DEAL_PROPERTIES + (properties or [])))
        body: dict[str, Any] = {
            "properties": props,
            "limit": limit,
        }
        if query:
            body["query"] = query
        if filters:
            body["filterGroups"] = [{"filters": filters}]
        if after:
            body["after"] = after
        return self.post("/crm/v3/objects/deals/search", json=body)

    # Companies
    def list_companies(
        self,
        limit: int = 20,
        after: str | None = None,
        properties: list[str] | None = None,
    ) -> dict:
        """List companies with pagination."""
        props = list(dict.fromkeys(DEFAULT_COMPANY_PROPERTIES + (properties or [])))
        params: dict[str, Any] = {
            "limit": limit,
            "properties": ",".join(props),
        }
        if after:
            params["after"] = after
        return self.get("/crm/v3/objects/companies", params=params)

    def get_company(self, company_id: str, properties: list[str] | None = None) -> dict:
        """Get a company by ID."""
        props = list(dict.fromkeys(DEFAULT_COMPANY_PROPERTIES + (properties or [])))
        params = {"properties": ",".join(props)}
        return self.get(f"/crm/v3/objects/companies/{company_id}", params=params)

    def create_company(self, properties: dict[str, str]) -> dict:
        """Create a new company."""
        return self.post("/crm/v3/objects/companies", json={"properties": properties})

    def update_company(self, company_id: str, properties: dict[str, str]) -> dict:
        """Update a company."""
        return self.patch(
            f"/crm/v3/objects/companies/{company_id}",
            json={"properties": properties},
        )

    def delete_company(self, company_id: str) -> None:
        """Delete (archive) a company."""
        self.delete(f"/crm/v3/objects/companies/{company_id}")

    def search_companies(
        self,
        query: str | None = None,
        filters: list[dict] | None = None,
        properties: list[str] | None = None,
        limit: int = 20,
        after: str | None = None,
    ) -> dict:
        """Search companies."""
        props = list(dict.fromkeys(DEFAULT_COMPANY_PROPERTIES + (properties or [])))
        body: dict[str, Any] = {
            "properties": props,
            "limit": limit,
        }
        if query:
            body["query"] = query
        if filters:
            body["filterGroups"] = [{"filters": filters}]
        if after:
            body["after"] = after
        return self.post("/crm/v3/objects/companies/search", json=body)

    # Pipelines
    def get_deal_pipelines(self) -> list[dict]:
        """Get all deal pipelines."""
        result = self.get("/crm/v3/pipelines/deals")
        return result.get("results", [])

    def get_pipeline_stages(self, pipeline_id: str) -> list[dict]:
        """Get stages for a pipeline."""
        result = self.get(f"/crm/v3/pipelines/deals/{pipeline_id}/stages")
        return result.get("results", [])

    # Owners
    def list_owners(self, limit: int = 100) -> list[dict]:
        """List owners (users)."""
        result = self.get("/crm/v3/owners", params={"limit": limit})
        return result.get("results", [])

    # Notes
    def create_note(self, body: str) -> dict:
        """Create a note object."""
        return self.post(
            "/crm/v3/objects/notes",
            json={
                "properties": {
                    "hs_note_body": body,
                    "hs_timestamp": str(int(time.time() * 1000)),
                }
            },
        )

    def associate_note(self, note_id: str, object_type: str, object_id: str) -> None:
        """Associate a note with a CRM object using v4 default associations."""
        self.put(
            f"/crm/v4/objects/note/{note_id}/associations/default/{object_type}/{object_id}",
        )

    def add_note(self, object_type: str, object_id: str, body: str) -> dict:
        """Create a note and associate it with a CRM object."""
        note = self.create_note(body)
        self.associate_note(note["id"], object_type, object_id)
        return note

    def list_notes(self, object_type: str, object_id: str) -> list[dict]:
        """List notes associated with a CRM object."""
        result = self.get(
            f"/crm/v4/objects/{object_type}/{object_id}/associations/notes",
        )
        note_ids = [r["toObjectId"] for r in result.get("results", [])]
        if not note_ids:
            return []
        batch = self.post(
            "/crm/v3/objects/notes/batch/read",
            json={
                "inputs": [{"id": nid} for nid in note_ids],
                "properties": ["hs_note_body", "hs_timestamp"],
            },
        )
        return batch.get("results", [])

    def delete_note(self, note_id: str) -> None:
        """Delete a note."""
        self.delete(f"/crm/v3/objects/notes/{note_id}")
