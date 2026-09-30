"""HubSpot CRM API client."""

import re
import time
from typing import Any

import httpx

BASE_URL = "https://api.hubapi.com"

# Date-based HubSpot API version used in all endpoint paths
API_VERSION = "2026-09"

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

EMAIL_PROPERTIES = [
    "hs_timestamp",
    "hs_email_direction",
    "hs_email_status",
    "hs_email_subject",
    "hs_email_text",
    "hs_email_html",
    "hs_email_from_email",
    "hs_email_from_firstname",
    "hs_email_from_lastname",
    "hs_email_to_email",
    "hs_email_cc_email",
    "hs_email_bcc_email",
    "hubspot_owner_id",
]

# HubSpot-defined association type IDs from emails to other objects
EMAIL_ASSOCIATION_TYPE_IDS = {
    "contacts": 198,
    "companies": 186,
    "deals": 210,
}

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


class HubSpotAPIError(httpx.HTTPStatusError):
    """HTTP error from the HubSpot API, carrying the message HubSpot returned."""

    def __init__(self, error: httpx.HTTPStatusError) -> None:
        response = error.response
        try:
            body = response.json()
        except ValueError:
            body = None
        if not isinstance(body, dict):
            body = {}

        # Category such as VALIDATION_ERROR or MISSING_SCOPES
        self.category: str = body.get("category") or ""
        messages = [body.get("message") or ""]
        for detail in body.get("errors") or []:
            text = detail.get("message") if isinstance(detail, dict) else None
            if text and text not in messages[0]:
                messages.append(text)
        self.detail: str = "; ".join(m for m in messages if m)

        # Properties HubSpot requires but the request did not set
        match = re.search(
            r"required properties were missing: \[([^\]]*)\]", self.detail
        )
        self.missing_properties: list[str] = (
            [name.strip() for name in match.group(1).split(",") if name.strip()]
            if match
            else []
        )

        if self.detail:
            prefix = f"HTTP {response.status_code} {self.category}".strip()
            message = f"{prefix}: {self.detail}"
        else:
            message = str(error)
        super().__init__(message, request=error.request, response=response)


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
        json: dict | list | None = None,
    ) -> Any:
        """Make an authenticated request to HubSpot API."""
        url = f"{BASE_URL}{path}"
        response = self._client.request(method, url, params=params, json=json)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HubSpotAPIError(e) from e

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
        self, path: str, params: dict | None = None, json: dict | list | None = None
    ) -> Any:
        """Make a PUT request."""
        return self._request("PUT", path, params=params, json=json)

    def delete(self, path: str, params: dict | None = None) -> Any:
        """Make a DELETE request."""
        return self._request("DELETE", path, params=params)

    # Account
    def get_me(self) -> dict:
        """Get account info to verify token."""
        return self.get(f"/account-info/{API_VERSION}/details")

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
        return self.get(f"/crm/objects/{API_VERSION}/contacts", params=params)

    def get_contact(self, contact_id: str, properties: list[str] | None = None) -> dict:
        """Get a contact by ID or email."""
        props = list(dict.fromkeys(DEFAULT_CONTACT_PROPERTIES + (properties or [])))
        params = {"properties": ",".join(props)}
        return self.get(
            f"/crm/objects/{API_VERSION}/contacts/{contact_id}", params=params
        )

    def get_contact_by_email(
        self, email: str, properties: list[str] | None = None
    ) -> dict:
        """Get a contact by email address."""
        props = list(dict.fromkeys(DEFAULT_CONTACT_PROPERTIES + (properties or [])))
        params: dict[str, str] = {
            "properties": ",".join(props),
            "idProperty": "email",
        }
        return self.get(f"/crm/objects/{API_VERSION}/contacts/{email}", params=params)

    def create_contact(self, properties: dict[str, str]) -> dict:
        """Create a new contact."""
        return self.post(
            f"/crm/objects/{API_VERSION}/contacts", json={"properties": properties}
        )

    def update_contact(self, contact_id: str, properties: dict[str, str]) -> dict:
        """Update a contact."""
        return self.patch(
            f"/crm/objects/{API_VERSION}/contacts/{contact_id}",
            json={"properties": properties},
        )

    def delete_contact(self, contact_id: str) -> None:
        """Delete (archive) a contact."""
        self.delete(f"/crm/objects/{API_VERSION}/contacts/{contact_id}")

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
        return self.post(f"/crm/objects/{API_VERSION}/contacts/search", json=body)

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
        return self.get(f"/crm/objects/{API_VERSION}/deals", params=params)

    def get_deal(self, deal_id: str, properties: list[str] | None = None) -> dict:
        """Get a deal by ID."""
        props = list(dict.fromkeys(DEFAULT_DEAL_PROPERTIES + (properties or [])))
        params = {"properties": ",".join(props)}
        return self.get(f"/crm/objects/{API_VERSION}/deals/{deal_id}", params=params)

    def create_deal(self, properties: dict[str, str]) -> dict:
        """Create a new deal."""
        return self.post(
            f"/crm/objects/{API_VERSION}/deals", json={"properties": properties}
        )

    def update_deal(self, deal_id: str, properties: dict[str, str]) -> dict:
        """Update a deal."""
        return self.patch(
            f"/crm/objects/{API_VERSION}/deals/{deal_id}",
            json={"properties": properties},
        )

    def delete_deal(self, deal_id: str) -> None:
        """Delete (archive) a deal."""
        self.delete(f"/crm/objects/{API_VERSION}/deals/{deal_id}")

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
        return self.post(f"/crm/objects/{API_VERSION}/deals/search", json=body)

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
        return self.get(f"/crm/objects/{API_VERSION}/companies", params=params)

    def get_company(self, company_id: str, properties: list[str] | None = None) -> dict:
        """Get a company by ID."""
        props = list(dict.fromkeys(DEFAULT_COMPANY_PROPERTIES + (properties or [])))
        params = {"properties": ",".join(props)}
        return self.get(
            f"/crm/objects/{API_VERSION}/companies/{company_id}", params=params
        )

    def create_company(self, properties: dict[str, str]) -> dict:
        """Create a new company."""
        return self.post(
            f"/crm/objects/{API_VERSION}/companies", json={"properties": properties}
        )

    def update_company(self, company_id: str, properties: dict[str, str]) -> dict:
        """Update a company."""
        return self.patch(
            f"/crm/objects/{API_VERSION}/companies/{company_id}",
            json={"properties": properties},
        )

    def delete_company(self, company_id: str) -> None:
        """Delete (archive) a company."""
        self.delete(f"/crm/objects/{API_VERSION}/companies/{company_id}")

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
        return self.post(f"/crm/objects/{API_VERSION}/companies/search", json=body)

    # Properties
    def list_properties(self, object_type: str) -> list[dict]:
        """List the property definitions of an object type."""
        result = self.get(f"/crm/properties/{API_VERSION}/{object_type}")
        return result.get("results", [])

    def get_property(self, object_type: str, name: str) -> dict:
        """Get a single property definition, including its options."""
        return self.get(f"/crm/properties/{API_VERSION}/{object_type}/{name}")

    # Pipelines
    def get_deal_pipelines(self) -> list[dict]:
        """Get all deal pipelines."""
        result = self.get(f"/crm/pipelines/{API_VERSION}/deals")
        return result.get("results", [])

    def get_pipeline_stages(self, pipeline_id: str) -> list[dict]:
        """Get stages for a pipeline."""
        result = self.get(f"/crm/pipelines/{API_VERSION}/deals/{pipeline_id}/stages")
        return result.get("results", [])

    # Owners
    def list_owners(self, limit: int = 100) -> list[dict]:
        """List owners (users)."""
        result = self.get(f"/crm/owners/{API_VERSION}", params={"limit": limit})
        return result.get("results", [])

    # Notes
    def create_note(self, body: str) -> dict:
        """Create a note object."""
        return self.post(
            f"/crm/objects/{API_VERSION}/notes",
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
            f"/crm/objects/{API_VERSION}/notes/{note_id}/associations/default/{object_type}/{object_id}",
        )

    def add_note(self, object_type: str, object_id: str, body: str) -> dict:
        """Create a note and associate it with a CRM object."""
        note = self.create_note(body)
        self.associate_note(note["id"], object_type, object_id)
        return note

    def list_notes(self, object_type: str, object_id: str) -> list[dict]:
        """List notes associated with a CRM object."""
        result = self.get(
            f"/crm/objects/{API_VERSION}/{object_type}/{object_id}/associations/notes",
        )
        note_ids = [r["toObjectId"] for r in result.get("results", [])]
        if not note_ids:
            return []
        batch = self.post(
            f"/crm/objects/{API_VERSION}/notes/batch/read",
            json={
                "inputs": [{"id": nid} for nid in note_ids],
                "properties": ["hs_note_body", "hs_timestamp"],
            },
        )
        return batch.get("results", [])

    def delete_note(self, note_id: str) -> None:
        """Delete a note."""
        self.delete(f"/crm/objects/{API_VERSION}/notes/{note_id}")

    # Emails
    def add_email(
        self, object_type: str, object_id: str, properties: dict[str, str]
    ) -> dict:
        """Log an email and associate it with a CRM object."""
        return self.post(
            f"/crm/objects/{API_VERSION}/emails",
            json={
                "properties": properties,
                "associations": [
                    {
                        "to": {"id": object_id},
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": EMAIL_ASSOCIATION_TYPE_IDS[
                                    object_type
                                ],
                            }
                        ],
                    }
                ],
            },
        )

    def list_emails(self, object_type: str, object_id: str) -> list[dict]:
        """List emails associated with a CRM object, newest first."""
        email_ids: list[str] = []
        params: dict[str, Any] = {"limit": 500}
        while True:
            result = self.get(
                f"/crm/objects/{API_VERSION}/{object_type}/{object_id}"
                "/associations/emails",
                params=params,
            )
            email_ids.extend(str(r["toObjectId"]) for r in result.get("results", []))
            after = result.get("paging", {}).get("next", {}).get("after")
            if not after:
                break
            params["after"] = after
        if not email_ids:
            return []
        emails: list[dict] = []
        for start in range(0, len(email_ids), 100):
            batch = self.post(
                f"/crm/objects/{API_VERSION}/emails/batch/read",
                json={
                    "inputs": [{"id": eid} for eid in email_ids[start : start + 100]],
                    "properties": EMAIL_PROPERTIES,
                    "propertiesWithHistory": [],
                },
            )
            emails.extend(batch.get("results", []))
        emails.sort(
            key=lambda e: e.get("properties", {}).get("hs_timestamp") or "",
            reverse=True,
        )
        return emails

    def get_email(self, email_id: str) -> dict:
        """Get an email by ID."""
        return self.get(
            f"/crm/objects/{API_VERSION}/emails/{email_id}",
            params={"properties": ",".join(EMAIL_PROPERTIES)},
        )

    def delete_email(self, email_id: str) -> None:
        """Delete an email."""
        self.delete(f"/crm/objects/{API_VERSION}/emails/{email_id}")

    # Associations
    def associate(
        self,
        from_object_type: str,
        from_object_id: str,
        to_object_type: str,
        to_object_id: str,
        association_types: list[dict] | None = None,
    ) -> None:
        """Create an association between two CRM objects (v4).

        Without association_types, a default (unlabeled) association is created.
        With it (a list of {"associationCategory", "associationTypeId"} dicts),
        a labeled association is created instead.
        """
        if association_types:
            self.put(
                f"/crm/objects/{API_VERSION}/{from_object_type}/{from_object_id}"
                f"/associations/{to_object_type}/{to_object_id}",
                json=association_types,
            )
        else:
            self.put(
                f"/crm/objects/{API_VERSION}/{from_object_type}/{from_object_id}"
                f"/associations/default/{to_object_type}/{to_object_id}",
            )

    def get_association_labels(
        self, from_object_type: str, to_object_type: str
    ) -> list[dict]:
        """List association labels/types defined between two object types (v4)."""
        result = self.get(
            f"/crm/associations/{API_VERSION}/{from_object_type}/{to_object_type}/labels",
        )
        return result.get("results", [])

    def disassociate(
        self,
        from_object_type: str,
        from_object_id: str,
        to_object_type: str,
        to_object_id: str,
    ) -> None:
        """Remove all associations between two CRM objects (v4)."""
        self.delete(
            f"/crm/objects/{API_VERSION}/{from_object_type}/{from_object_id}"
            f"/associations/{to_object_type}/{to_object_id}",
        )

    def list_associations(
        self, object_type: str, object_id: str, to_object_type: str
    ) -> list[dict]:
        """List objects of to_object_type associated with a CRM object (v4)."""
        result = self.get(
            f"/crm/objects/{API_VERSION}/{object_type}/{object_id}/associations/{to_object_type}",
        )
        return result.get("results", [])

    def merge(self, object_type: str, primary_id: str, merge_id: str) -> dict:
        """Merge two records of the same type into one.

        ``primary_id`` is kept; ``merge_id`` is merged into it and then
        archived. Returns the resulting record, whose ID may differ from
        ``primary_id``. Supported object types include contacts, companies,
        and deals.
        """
        return self.post(
            f"/crm/objects/{API_VERSION}/{object_type}/merge",
            json={"primaryObjectId": primary_id, "objectIdToMerge": merge_id},
        )

    def batch_read(
        self,
        object_type: str,
        object_ids: list[str],
        properties: list[str] | None = None,
    ) -> list[dict]:
        """Batch read objects by ID.

        The HubSpot batch read endpoint accepts at most 100 IDs per request,
        so larger lists are fetched in chunks.
        """
        results: list[dict] = []
        for start in range(0, len(object_ids), 100):
            chunk = object_ids[start : start + 100]
            body: dict[str, Any] = {"inputs": [{"id": str(i)} for i in chunk]}
            if properties:
                body["properties"] = properties
            result = self.post(
                f"/crm/objects/{API_VERSION}/{object_type}/batch/read",
                json=body,
            )
            results.extend(result.get("results", []))
        return results
