from datetime import datetime, timedelta
from typing import Optional
from pydantic import Field, SecretStr, validator
from openai import OpenAI

from airtrain.core.credentials import BaseCredentials, CredentialValidationError


class OpenAICredentials(BaseCredentials):
    """OpenAI API credentials with enhanced validation"""

    openai_api_key: SecretStr = Field(..., description="OpenAI API key")
    openai_organization_id: Optional[str] = Field(
        None, description="OpenAI organization ID", pattern="^org-[A-Za-z0-9]{24}$"
    )

    _required_credentials = {"openai_api_key"}

    @validator("openai_api_key")
    def validate_api_key_format(cls, v: SecretStr) -> SecretStr:
        key = v.get_secret_value()
        if not key.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        if len(key) < 40:
            raise ValueError("OpenAI API key appears to be too short")
        return v

    async def validate_credentials(self) -> bool:
        """Validate credentials by making a test API call"""
        try:
            client = OpenAI(
                api_key=self.openai_api_key.get_secret_value(),
                organization=self.openai_organization_id,
            )
            # Make minimal API call to validate
            await client.models.list(limit=1)
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid OpenAI credentials: {str(e)}")
