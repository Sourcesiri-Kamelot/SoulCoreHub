from pydantic import Field, SecretStr
from airtrain.core.credentials import BaseCredentials, CredentialValidationError


class CerebrasCredentials(BaseCredentials):
    """Cerebras credentials"""

    cerebras_api_key: SecretStr = Field(..., description="Cerebras API key")

    _required_credentials = {"cerebras_api_key"}

    async def validate_credentials(self) -> bool:
        """Validate Cerebras credentials"""
        try:
            # Implement Cerebras-specific validation
            # This would depend on their API client implementation
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid Cerebras credentials: {str(e)}")
