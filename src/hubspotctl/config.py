"""Configuration management for HubSpot CLI."""

import json
import os
from pathlib import Path

import keyring

SERVICE_NAME = "hubspotctl"
ACCESS_TOKEN_ENV_VAR = "HUBSPOT_ACCESS_TOKEN"


class Config:
    """Manages HubSpot CLI configuration and credentials."""

    def __init__(self, profile: str = "default") -> None:
        self.profile = profile
        self.config_dir = Path.home() / ".config" / "hubspotctl"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / f"{profile}.json"

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            return json.loads(self.config_file.read_text())
        return {}

    def _save_config(self, config: dict) -> None:
        """Save configuration to file."""
        self.config_file.write_text(json.dumps(config, indent=2))

    def get_token(self) -> str | None:
        """Get the access token from the environment or keyring."""
        return os.environ.get(ACCESS_TOKEN_ENV_VAR) or keyring.get_password(
            SERVICE_NAME, f"{self.profile}:token"
        )

    def set_token(self, token: str) -> None:
        """Store the access token in keyring."""
        keyring.set_password(SERVICE_NAME, f"{self.profile}:token", token)

    def is_configured(self) -> bool:
        """Check if credentials are configured."""
        return bool(self.get_token())
