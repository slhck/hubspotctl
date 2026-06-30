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

    def test_merge(self, cli: Any) -> None:
        runner, client, _ = cli
        client.merge.return_value = {"id": "999", "properties": {}}
        result = runner.invoke(main, ["contact", "merge", "101", "102", "--yes"])
        assert result.exit_code == 0
        assert "Merged contact 102 into contact 101" in result.output
        assert "resulting contact: 999" in result.output
        client.merge.assert_called_once_with("contacts", "101", "102")

    def test_merge_aborts_without_confirmation(self, cli: Any) -> None:
        runner, client, _ = cli
        result = runner.invoke(main, ["contact", "merge", "101", "102"], input="n\n")
        assert result.exit_code != 0
        client.merge.assert_not_called()


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
            {
                "id": "501",
                "properties": {
                    "hs_note_body": "Note 1",
                    "hs_timestamp": "1700000000000",
                },
            },
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


class TestContactAssociationCommands:
    def test_associate(self, cli: Any) -> None:
        runner, client, _ = cli
        client.associate.return_value = None
        result = runner.invoke(
            main, ["contact", "associate", "101", "--company", "301", "--deal", "201"]
        )
        assert result.exit_code == 0
        client.associate.assert_any_call("contacts", "101", "companies", "301")
        client.associate.assert_any_call("contacts", "101", "deals", "201")

    def test_disassociate(self, cli: Any) -> None:
        runner, client, _ = cli
        client.disassociate.return_value = None
        result = runner.invoke(
            main, ["contact", "disassociate", "101", "--deal", "201"]
        )
        assert result.exit_code == 0
        assert "Disassociated contact 101 from deal 201" in result.output

    def test_associate_requires_target(self, cli: Any) -> None:
        runner, client, _ = cli
        result = runner.invoke(main, ["contact", "associate", "101"])
        assert "Specify at least one" in result.output
        client.associate.assert_not_called()

    def test_associations(self, cli: Any) -> None:
        runner, client, _ = cli
        client.list_associations.side_effect = [
            [{"toObjectId": "301"}],
            [{"toObjectId": "201"}],
        ]
        client.batch_read.side_effect = [
            [{"id": "301", "properties": {"name": "Acme Inc"}}],
            [{"id": "201", "properties": {"dealname": "Enterprise License"}}],
        ]
        result = runner.invoke(main, ["contact", "associations", "101"])
        assert result.exit_code == 0
        assert "Acme Inc" in result.output
        assert "Enterprise License" in result.output


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

    def test_merge(self, cli: Any) -> None:
        runner, client, _ = cli
        client.merge.return_value = {"id": "301", "properties": {}}
        result = runner.invoke(main, ["company", "merge", "301", "302", "--yes"])
        assert result.exit_code == 0
        assert "Merged company 302 into company 301" in result.output
        client.merge.assert_called_once_with("companies", "301", "302")


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
            {
                "id": "502",
                "properties": {
                    "hs_note_body": "Company note",
                    "hs_timestamp": "1700000000000",
                },
            },
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


class TestCompanyAssociationCommands:
    def test_associate(self, cli: Any) -> None:
        runner, client, _ = cli
        client.associate.return_value = None
        result = runner.invoke(
            main, ["company", "associate", "301", "--contact", "101", "--deal", "201"]
        )
        assert result.exit_code == 0
        client.associate.assert_any_call("companies", "301", "contacts", "101")
        client.associate.assert_any_call("companies", "301", "deals", "201")

    def test_disassociate(self, cli: Any) -> None:
        runner, client, _ = cli
        client.disassociate.return_value = None
        result = runner.invoke(
            main, ["company", "disassociate", "301", "--contact", "101"]
        )
        assert result.exit_code == 0
        assert "Disassociated company 301 from contact 101" in result.output

    def test_associations(self, cli: Any) -> None:
        runner, client, _ = cli
        client.list_associations.side_effect = [
            [{"toObjectId": "101"}],
            [{"toObjectId": "201"}],
        ]
        client.batch_read.side_effect = [
            [
                {
                    "id": "101",
                    "properties": {
                        "firstname": "John",
                        "lastname": "Doe",
                        "email": "john@example.com",
                    },
                }
            ],
            [{"id": "201", "properties": {"dealname": "Enterprise License"}}],
        ]
        result = runner.invoke(main, ["company", "associations", "301"])
        assert result.exit_code == 0
        assert "John Doe <john@example.com>" in result.output
        assert "Enterprise License" in result.output


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

    def test_merge(self, cli: Any) -> None:
        runner, client, _ = cli
        client.merge.return_value = {"id": "201", "properties": {}}
        result = runner.invoke(main, ["deal", "merge", "201", "202", "--yes"])
        assert result.exit_code == 0
        assert "Merged deal 202 into deal 201" in result.output
        client.merge.assert_called_once_with("deals", "201", "202")


class TestDealNoteCommands:
    def test_add_note(self, cli: Any) -> None:
        runner, client, _ = cli
        client.add_note.return_value = {"id": "503", "properties": {}}
        result = runner.invoke(main, ["deal", "add-note", "201", "--body", "Deal note"])
        assert result.exit_code == 0
        assert "Added note 503" in result.output
        client.add_note.assert_called_once_with("deals", "201", "Deal note")

    def test_notes(self, cli: Any) -> None:
        runner, client, _ = cli
        client.list_notes.return_value = [
            {
                "id": "503",
                "properties": {
                    "hs_note_body": "Deal note",
                    "hs_timestamp": "1700000000000",
                },
            },
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


class TestDealAssociationCommands:
    def test_associate(self, cli: Any) -> None:
        runner, client, _ = cli
        client.associate.return_value = None
        result = runner.invoke(
            main,
            ["deal", "associate", "201", "--company", "301", "--contact", "101"],
        )
        assert result.exit_code == 0
        assert "company 301" in result.output
        assert "contact 101" in result.output
        client.associate.assert_any_call("deals", "201", "companies", "301")
        client.associate.assert_any_call("deals", "201", "contacts", "101")

    def test_associate_multiple_contacts(self, cli: Any) -> None:
        runner, client, _ = cli
        client.associate.return_value = None
        result = runner.invoke(
            main,
            ["deal", "associate", "201", "-C", "101", "-C", "102"],
        )
        assert result.exit_code == 0
        assert client.associate.call_count == 2

    def test_associate_requires_target(self, cli: Any) -> None:
        runner, client, _ = cli
        result = runner.invoke(main, ["deal", "associate", "201"])
        assert "Specify at least one" in result.output
        client.associate.assert_not_called()

    def test_disassociate(self, cli: Any) -> None:
        runner, client, _ = cli
        client.disassociate.return_value = None
        result = runner.invoke(
            main, ["deal", "disassociate", "201", "--company", "301"]
        )
        assert result.exit_code == 0
        assert "Disassociated deal 201 from company 301" in result.output
        client.disassociate.assert_called_once_with("deals", "201", "companies", "301")

    def test_disassociate_requires_target(self, cli: Any) -> None:
        runner, client, _ = cli
        result = runner.invoke(main, ["deal", "disassociate", "201"])
        assert "Specify at least one" in result.output
        client.disassociate.assert_not_called()

    def test_associations(self, cli: Any) -> None:
        runner, client, _ = cli
        client.list_associations.side_effect = [
            [
                {
                    "toObjectId": "301",
                    "associationTypes": [
                        {
                            "category": "HUBSPOT_DEFINED",
                            "typeId": 5,
                            "label": "Primary",
                        },
                        {"category": "HUBSPOT_DEFINED", "typeId": 341, "label": None},
                    ],
                }
            ],
            [
                {
                    "toObjectId": "101",
                    "associationTypes": [
                        {"category": "HUBSPOT_DEFINED", "typeId": 3, "label": None},
                    ],
                }
            ],
        ]
        client.batch_read.side_effect = [
            [{"id": "301", "properties": {"name": "Acme Inc"}}],
            [
                {
                    "id": "101",
                    "properties": {
                        "firstname": "John",
                        "lastname": "Doe",
                        "email": "john@example.com",
                    },
                }
            ],
        ]
        result = runner.invoke(
            main, ["--format", "json", "deal", "associations", "201"]
        )
        assert result.exit_code == 0
        assert "Acme Inc" in result.output
        assert "John Doe <john@example.com>" in result.output
        # The labeled company shows its label; the unlabeled contact does not.
        assert "Primary" in result.output
        assert "None" not in result.output

    def test_associate_with_label_by_name(self, cli: Any) -> None:
        runner, client, _ = cli
        client.get_association_labels.return_value = [
            {"category": "USER_DEFINED", "typeId": 36, "label": "Decision maker"},
        ]
        client.associate.return_value = None
        result = runner.invoke(
            main,
            [
                "deal",
                "associate",
                "201",
                "--company",
                "301",
                "--label",
                "Decision maker",
            ],
        )
        assert result.exit_code == 0
        assert "[Decision maker]" in result.output
        client.associate.assert_called_once_with(
            "deals",
            "201",
            "companies",
            "301",
            association_types=[
                {"associationCategory": "USER_DEFINED", "associationTypeId": 36}
            ],
        )

    def test_associate_with_label_by_type_id(self, cli: Any) -> None:
        runner, client, _ = cli
        client.get_association_labels.return_value = [
            {"category": "HUBSPOT_DEFINED", "typeId": 5, "label": "Primary"},
        ]
        client.associate.return_value = None
        result = runner.invoke(
            main, ["deal", "associate", "201", "--company", "301", "--label", "5"]
        )
        assert result.exit_code == 0
        client.associate.assert_called_once_with(
            "deals",
            "201",
            "companies",
            "301",
            association_types=[
                {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}
            ],
        )

    def test_associate_unknown_label(self, cli: Any) -> None:
        runner, client, _ = cli
        client.get_association_labels.return_value = [
            {"category": "HUBSPOT_DEFINED", "typeId": 5, "label": "Primary"},
        ]
        result = runner.invoke(
            main, ["deal", "associate", "201", "--company", "301", "--label", "Nope"]
        )
        assert "Unknown label 'Nope'" in result.output
        client.associate.assert_not_called()

    def test_labels(self, cli: Any) -> None:
        runner, client, _ = cli
        client.get_association_labels.side_effect = [
            [{"category": "HUBSPOT_DEFINED", "typeId": 5, "label": "Primary"}],
            [{"category": "USER_DEFINED", "typeId": 40, "label": "Champion"}],
        ]
        result = runner.invoke(main, ["deal", "labels"])
        assert result.exit_code == 0
        assert "Primary" in result.output
        assert "Champion" in result.output


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
