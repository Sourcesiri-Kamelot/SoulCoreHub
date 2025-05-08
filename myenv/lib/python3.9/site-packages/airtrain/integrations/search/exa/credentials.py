"""
Credentials for Exa Search API.

This module provides credential management for the Exa search API.
"""

from typing import Optional
from pydantic import Field, SecretStr

from airtrain.core.credentials import BaseCredentials


class ExaCredentials(BaseCredentials):
    """Credentials for accessing the Exa search API."""

    exa_api_key: SecretStr = Field(
        description="Exa search API key",
    )

    _required_credentials = {"exa_api_key"}

    async def validate_credentials(self) -> bool:
        """Validate that the required credentials are present and valid."""
        # First check that required credentials are present
        await super().validate_credentials()

        # In a production environment, we might want to make a test API call here
        # to verify the API key is actually valid, but for now we'll just check
        # that it's present
        return True
