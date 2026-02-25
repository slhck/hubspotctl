"""Tests for the CLI commands."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from hubspotctl.cli import main


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for the main CLI."""

    def test_help(self, runner: CliRunner) -> None:
        """Test --help flag."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "hubspotctl" in result.output
        assert "contact" in result.output
        assert "deal" in result.output
        assert "auth" in result.output


class TestContactCommands:
    """Tests for contact commands."""

    def test_contact_list(
        self, runner: CliRunner, mock_contacts: list[dict], mocker: Any
    ) -> None:
        """Test contact list command."""
        mock_client = MagicMock()
        mock_client.list_contacts.return_value = {"results": mock_contacts}

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["contact", "list"])

        assert result.exit_code == 0
        assert "John" in result.output
        assert "Jane" in result.output

    def test_contact_list_json(
        self, runner: CliRunner, mock_contacts: list[dict], mocker: Any
    ) -> None:
        """Test contact list with JSON output."""
        mock_client = MagicMock()
        mock_client.list_contacts.return_value = {"results": mock_contacts}

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["--format", "json", "contact", "list"])

        assert result.exit_code == 0
        assert '"email": "john@example.com"' in result.output

    def test_contact_show(
        self, runner: CliRunner, mock_contacts: list[dict], mocker: Any
    ) -> None:
        """Test contact show command."""
        mock_client = MagicMock()
        mock_client.get_contact.return_value = mock_contacts[0]

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(
                    main, ["--format", "json", "contact", "show", "101"]
                )

        assert result.exit_code == 0
        assert "John" in result.output

    def test_contact_show_by_email(
        self, runner: CliRunner, mock_contacts: list[dict], mocker: Any
    ) -> None:
        """Test contact show by email."""
        mock_client = MagicMock()
        mock_client.get_contact_by_email.return_value = mock_contacts[0]

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(
                    main,
                    ["--format", "json", "contact", "show", "john@example.com"],
                )

        assert result.exit_code == 0
        mock_client.get_contact_by_email.assert_called_once()

    def test_contact_search(
        self, runner: CliRunner, mock_contacts: list[dict], mocker: Any
    ) -> None:
        """Test contact search command."""
        mock_client = MagicMock()
        mock_client.search_contacts.return_value = {
            "results": [mock_contacts[0]],
            "total": 1,
        }

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["contact", "search", "john"])

        assert result.exit_code == 0
        assert "John" in result.output

    def test_contact_create(self, runner: CliRunner, mocker: Any) -> None:
        """Test contact create command."""
        mock_client = MagicMock()
        mock_client.create_contact.return_value = {
            "id": "103",
            "properties": {"email": "new@example.com"},
        }

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(
                    main,
                    ["contact", "create", "--email", "new@example.com", "--firstname", "New"],
                )

        assert result.exit_code == 0
        assert "Created contact" in result.output

    def test_contact_update(self, runner: CliRunner, mocker: Any) -> None:
        """Test contact update command."""
        mock_client = MagicMock()
        mock_client.update_contact.return_value = {
            "id": "101",
            "properties": {"firstname": "Updated"},
        }

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(
                    main, ["contact", "update", "101", "--firstname", "Updated"]
                )

        assert result.exit_code == 0
        assert "Updated contact" in result.output

    def test_contact_update_no_changes(self, runner: CliRunner, mocker: Any) -> None:
        """Test contact update with no changes."""
        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient"):
                result = runner.invoke(main, ["contact", "update", "101"])

        assert "No updates specified" in result.output


class TestDealCommands:
    """Tests for deal commands."""

    def test_deal_list(
        self, runner: CliRunner, mock_deals: list[dict], mocker: Any
    ) -> None:
        """Test deal list command."""
        mock_client = MagicMock()
        mock_client.list_deals.return_value = {"results": mock_deals}

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["--format", "json", "deal", "list"])

        assert result.exit_code == 0
        assert "Enterprise License" in result.output
        assert "Starter Plan" in result.output

    def test_deal_show(
        self, runner: CliRunner, mock_deals: list[dict], mocker: Any
    ) -> None:
        """Test deal show command."""
        mock_client = MagicMock()
        mock_client.get_deal.return_value = mock_deals[0]

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(
                    main, ["--format", "json", "deal", "show", "201"]
                )

        assert result.exit_code == 0
        assert "Enterprise License" in result.output

    def test_deal_search(
        self, runner: CliRunner, mock_deals: list[dict], mocker: Any
    ) -> None:
        """Test deal search command."""
        mock_client = MagicMock()
        mock_client.search_deals.return_value = {
            "results": [mock_deals[0]],
            "total": 1,
        }

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["--format", "json", "deal", "search", "enterprise"])

        assert result.exit_code == 0
        assert "Enterprise License" in result.output

    def test_deal_create(self, runner: CliRunner, mocker: Any) -> None:
        """Test deal create command."""
        mock_client = MagicMock()
        mock_client.create_deal.return_value = {
            "id": "203",
            "properties": {"dealname": "New Deal"},
        }

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(
                    main,
                    [
                        "deal",
                        "create",
                        "--name",
                        "New Deal",
                        "--stage",
                        "qualifiedtobuy",
                    ],
                )

        assert result.exit_code == 0
        assert "Created deal" in result.output

    def test_deal_update(self, runner: CliRunner, mocker: Any) -> None:
        """Test deal update command."""
        mock_client = MagicMock()
        mock_client.update_deal.return_value = {
            "id": "201",
            "properties": {"amount": "75000"},
        }

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(
                    main, ["deal", "update", "201", "--amount", "75000"]
                )

        assert result.exit_code == 0
        assert "Updated deal" in result.output

    def test_deal_stages(
        self, runner: CliRunner, mock_pipelines: list[dict], mocker: Any
    ) -> None:
        """Test deal stages command."""
        mock_client = MagicMock()
        mock_client.get_deal_pipelines.return_value = mock_pipelines

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["deal", "stages"])

        assert result.exit_code == 0
        assert "Sales Pipeline" in result.output
        assert "Contract Sent" in result.output

    def test_deal_owners(
        self, runner: CliRunner, mock_owners: list[dict], mocker: Any
    ) -> None:
        """Test deal owners command."""
        mock_client = MagicMock()
        mock_client.list_owners.return_value = mock_owners

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["deal", "owners"])

        assert result.exit_code == 0
        assert "owner@example.com" in result.output


class TestAuthCommands:
    """Tests for auth commands."""

    def test_auth_status_not_configured(self, runner: CliRunner, mocker: Any) -> None:
        """Test auth status when not configured."""
        mock_config = MagicMock()
        mock_config.is_configured.return_value = False

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            result = runner.invoke(main, ["auth", "status"])

        assert "Not authenticated" in result.output

    def test_auth_logout(self, runner: CliRunner, mocker: Any) -> None:
        """Test auth logout command."""
        mock_config = MagicMock()

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("keyring.delete_password"):
                result = runner.invoke(main, ["auth", "logout"])

        assert result.exit_code == 0
        assert "Credentials removed" in result.output


class TestOutputFormats:
    """Tests for different output formats."""

    def test_csv_output(
        self, runner: CliRunner, mock_contacts: list[dict], mocker: Any
    ) -> None:
        """Test CSV output format."""
        mock_client = MagicMock()
        mock_client.list_contacts.return_value = {"results": mock_contacts}

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["--format", "csv", "contact", "list"])

        assert result.exit_code == 0
        assert "id" in result.output
        assert "john@example.com" in result.output

    def test_plain_output(
        self, runner: CliRunner, mock_contacts: list[dict], mocker: Any
    ) -> None:
        """Test plain output format."""
        mock_client = MagicMock()
        mock_client.list_contacts.return_value = {"results": mock_contacts}

        mock_config = MagicMock()
        mock_config.get_token.return_value = "test_token"

        with patch("hubspotctl.cli.Config", return_value=mock_config):
            with patch("hubspotctl.cli.HubSpotClient", return_value=mock_client):
                result = runner.invoke(main, ["--format", "plain", "contact", "list"])

        assert result.exit_code == 0
        assert "John" in result.output
