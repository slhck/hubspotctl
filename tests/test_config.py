"""Tests for configuration and credential resolution."""

from __future__ import annotations

from typing import Any

from hubspotctl.config import ACCESS_TOKEN_ENV_VAR, Config, SERVICE_NAME


def test_environment_token_takes_precedence(
    monkeypatch: Any, mocker: Any, tmp_path: Any
) -> None:
    monkeypatch.setenv(ACCESS_TOKEN_ENV_VAR, "environment_token")
    mocker.patch("hubspotctl.config.Path.home", return_value=tmp_path)
    get_password = mocker.patch(
        "hubspotctl.config.keyring.get_password", return_value="keyring_token"
    )

    assert Config("work").get_token() == "environment_token"
    get_password.assert_not_called()


def test_empty_environment_token_falls_back_to_keyring(
    monkeypatch: Any, mocker: Any, tmp_path: Any
) -> None:
    monkeypatch.setenv(ACCESS_TOKEN_ENV_VAR, "")
    mocker.patch("hubspotctl.config.Path.home", return_value=tmp_path)
    get_password = mocker.patch(
        "hubspotctl.config.keyring.get_password", return_value="keyring_token"
    )

    assert Config("work").get_token() == "keyring_token"
    get_password.assert_called_once_with(SERVICE_NAME, "work:token")
