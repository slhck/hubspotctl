"""Tests for the CLI commands."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from click.testing import CliRunner

from hubspotctl.cli import main


class TestCLI:
    def test_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        for group in ("auth", "company", "contact", "deal"):
            assert group in result.output


class TestContactCommands:
    def test_list(self, cli: Any, mock_contacts: list[dict]) -> None:
        runner, client, _ = cli
        client.list_contacts.return_value = {"results": mock_contacts}
        result = runner.invoke(main, ["contact", "list"])
        assert result.exit_code == 0
        assert "John" in result.output

    def test_show(self, cli: Any, mock_contacts: list[dict]) -> None:
        runner, client, _ = cli
        client.get_contact.return_value = mock_contacts[0]
        result = runner.invoke(main, ["--format", "json", "contact", "show", "101"])
        assert result.exit_code == 0
        assert "John" in result.output

    def test_show_by_email(self, cli: Any, mock_contacts: list[dict]) -> None:
        runner, client, _ = cli
        client.get_contact_by_email.return_value = mock_contacts[0]
        result = runner.invoke(main, ["contact", "show", "john@example.com"])
        assert result.exit_code == 0
        client.get_contact_by_email.assert_called_once()

    def test_search(self, cli: Any, mock_contacts: list[dict]) -> None:
        runner, client, _ = cli
        client.search_contacts.return_value = {
            "results": [mock_contacts[0]],
            "total": 1,
        }
        result = runner.invoke(main, ["contact", "search", "john"])
        assert result.exit_code == 0
        assert "John" in result.output

    def test_create(self, cli: Any) -> None:
        runner, client, _ = cli
        client.create_contact.return_value = {"id": "103", "properties": {}}
        result = runner.invoke(
            main, ["contact", "create", "--email", "new@example.com"]
        )
        assert result.exit_code == 0
        assert "Created contact" in result.output

    def test_update(self, cli: Any) -> None:
        runner, client, _ = cli
        client.update_contact.return_value = {"id": "101", "properties": {}}
        result = runner.invoke(
            main, ["contact", "update", "101", "--firstname", "Updated"]
        )
        assert result.exit_code == 0
        assert "Updated contact" in result.output

    def test_update_no_changes(self, cli: Any) -> None:
        runner, _, _ = cli
        result = runner.invoke(main, ["contact", "update", "101"])
        assert "No updates specified" in result.output


class TestContactNoteCommands:
    def test_add_note(self, cli: Any) -> None:
        runner, client, _ = cli
        client.add_note.return_value = {"id": "501", "properties": {}}
        result = runner.invoke(
            main, ["contact", "add-note", "101", "--body", "Test note"]
        )
        assert result.exit_code == 0
        assert "Added note 501" in result.output
        client.add_note.assert_called_once_with("contacts", "101", "Test note")

    def test_notes(self, cli: Any) -> None:
        runner, client, _ = cli
        client.list_notes.return_value = [
            {"id": "501", "properties": {"hs_note_body": "Note 1", "hs_timestamp": "1700000000000"}},
        ]
        result = runner.invoke(main, ["contact", "notes", "101"])
        assert result.exit_code == 0
        assert "Note 1" in result.output

    def test_delete_note(self, cli: Any) -> None:
        runner, client, _ = cli
        client.delete_note.return_value = None
        result = runner.invoke(main, ["contact", "delete-note", "501", "--yes"])
        assert result.exit_code == 0
        assert "Deleted note" in result.output


class TestCompanyCommands:
    def test_list(self, cli: Any, mock_companies: list[dict]) -> None:
        runner, client, _ = cli
        client.list_companies.return_value = {"results": mock_companies}
        result = runner.invoke(main, ["company", "list"])
        assert result.exit_code == 0
        assert "Acme" in result.output

    def test_show(self, cli: Any, mock_companies: list[dict]) -> None:
        runner, client, _ = cli
        client.get_company.return_value = mock_companies[0]
        result = runner.invoke(main, ["--format", "json", "company", "show", "301"])
        assert result.exit_code == 0
        assert "Acme" in result.output

    def test_search(self, cli: Any, mock_companies: list[dict]) -> None:
        runner, client, _ = cli
        client.search_companies.return_value = {
            "results": [mock_companies[0]],
            "total": 1,
        }
        result = runner.invoke(main, ["company", "search", "acme"])
        assert result.exit_code == 0
        assert "Acme" in result.output

    def test_create(self, cli: Any) -> None:
        runner, client, _ = cli
        client.create_company.return_value = {"id": "303", "properties": {}}
        result = runner.invoke(main, ["company", "create", "--name", "New Corp"])
        assert result.exit_code == 0
        assert "Created company" in result.output

    def test_update(self, cli: Any) -> None:
        runner, client, _ = cli
        client.update_company.return_value = {"id": "301", "properties": {}}
        result = runner.invoke(main, ["company", "update", "301", "--name", "Updated"])
        assert result.exit_code == 0
        assert "Updated company" in result.output

    def test_update_no_changes(self, cli: Any) -> None:
        runner, _, _ = cli
        result = runner.invoke(main, ["company", "update", "301"])
        assert "No updates specified" in result.output


class TestCompanyNoteCommands:
    def test_add_note(self, cli: Any) -> None:
        runner, client, _ = cli
        client.add_note.return_value = {"id": "502", "properties": {}}
        result = runner.invoke(
            main, ["company", "add-note", "301", "--body", "Company note"]
        )
        assert result.exit_code == 0
        assert "Added note 502" in result.output
        client.add_note.assert_called_once_with("companies", "301", "Company note")

    def test_notes(self, cli: Any) -> None:
        runner, client, _ = cli
        client.list_notes.return_value = [
            {"id": "502", "properties": {"hs_note_body": "Company note", "hs_timestamp": "1700000000000"}},
        ]
        result = runner.invoke(main, ["company", "notes", "301"])
        assert result.exit_code == 0
        assert "Company note" in result.output

    def test_delete_note(self, cli: Any) -> None:
        runner, client, _ = cli
        client.delete_note.return_value = None
        result = runner.invoke(main, ["company", "delete-note", "502", "--yes"])
        assert result.exit_code == 0
        assert "Deleted note" in result.output


class TestDealCommands:
    def test_list(self, cli: Any, mock_deals: list[dict]) -> None:
        runner, client, _ = cli
        client.list_deals.return_value = {"results": mock_deals}
        result = runner.invoke(main, ["--format", "json", "deal", "list"])
        assert result.exit_code == 0
        assert "Enterprise License" in result.output

    def test_show(self, cli: Any, mock_deals: list[dict]) -> None:
        runner, client, _ = cli
        client.get_deal.return_value = mock_deals[0]
        result = runner.invoke(main, ["--format", "json", "deal", "show", "201"])
        assert result.exit_code == 0
        assert "Enterprise License" in result.output

    def test_search(self, cli: Any, mock_deals: list[dict]) -> None:
        runner, client, _ = cli
        client.search_deals.return_value = {"results": [mock_deals[0]], "total": 1}
        result = runner.invoke(
            main, ["--format", "json", "deal", "search", "enterprise"]
        )
        assert result.exit_code == 0
        assert "Enterprise License" in result.output

    def test_create(self, cli: Any) -> None:
        runner, client, _ = cli
        client.create_deal.return_value = {"id": "203", "properties": {}}
        result = runner.invoke(
            main, ["deal", "create", "--name", "New Deal", "--stage", "qualifiedtobuy"]
        )
        assert result.exit_code == 0
        assert "Created deal" in result.output

    def test_update(self, cli: Any) -> None:
        runner, client, _ = cli
        client.update_deal.return_value = {"id": "201", "properties": {}}
        result = runner.invoke(main, ["deal", "update", "201", "--amount", "75000"])
        assert result.exit_code == 0
        assert "Updated deal" in result.output

    def test_stages(self, cli: Any, mock_pipelines: list[dict]) -> None:
        runner, client, _ = cli
        client.get_deal_pipelines.return_value = mock_pipelines
        result = runner.invoke(main, ["deal", "stages"])
        assert result.exit_code == 0
        assert "Sales Pipeline" in result.output

    def test_owners(self, cli: Any, mock_owners: list[dict]) -> None:
        runner, client, _ = cli
        client.list_owners.return_value = mock_owners
        result = runner.invoke(main, ["deal", "owners"])
        assert result.exit_code == 0
        assert "owner@example.com" in result.output


class TestDealNoteCommands:
    def test_add_note(self, cli: Any) -> None:
        runner, client, _ = cli
        client.add_note.return_value = {"id": "503", "properties": {}}
        result = runner.invoke(
            main, ["deal", "add-note", "201", "--body", "Deal note"]
        )
        assert result.exit_code == 0
        assert "Added note 503" in result.output
        client.add_note.assert_called_once_with("deals", "201", "Deal note")

    def test_notes(self, cli: Any) -> None:
        runner, client, _ = cli
        client.list_notes.return_value = [
            {"id": "503", "properties": {"hs_note_body": "Deal note", "hs_timestamp": "1700000000000"}},
        ]
        result = runner.invoke(main, ["deal", "notes", "201"])
        assert result.exit_code == 0
        assert "Deal note" in result.output

    def test_delete_note(self, cli: Any) -> None:
        runner, client, _ = cli
        client.delete_note.return_value = None
        result = runner.invoke(main, ["deal", "delete-note", "503", "--yes"])
        assert result.exit_code == 0
        assert "Deleted note" in result.output


class TestAuthCommands:
    def test_status_not_configured(self, cli: Any) -> None:
        runner, _, config = cli
        config.is_configured.return_value = False
        result = runner.invoke(main, ["auth", "status"])
        assert "Not authenticated" in result.output

    def test_logout(self, cli: Any) -> None:
        runner, _, _ = cli
        with patch("keyring.delete_password"):
            result = runner.invoke(main, ["auth", "logout"])
        assert result.exit_code == 0
        assert "Credentials removed" in result.output


class TestOutputFormats:
    def test_csv(self, cli: Any, mock_contacts: list[dict]) -> None:
        runner, client, _ = cli
        client.list_contacts.return_value = {"results": mock_contacts}
        result = runner.invoke(main, ["--format", "csv", "contact", "list"])
        assert result.exit_code == 0
        assert "john@example.com" in result.output

    def test_plain(self, cli: Any, mock_contacts: list[dict]) -> None:
        runner, client, _ = cli
        client.list_contacts.return_value = {"results": mock_contacts}
        result = runner.invoke(main, ["--format", "plain", "contact", "list"])
        assert result.exit_code == 0
        assert "John" in result.output
