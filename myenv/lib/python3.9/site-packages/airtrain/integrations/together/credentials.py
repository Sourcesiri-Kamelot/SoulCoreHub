from pydantic import Field, SecretStr
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
import together


class TogetherAICredentials(BaseCredentials):
    """Together AI credentials"""

    together_api_key: SecretStr = Field(..., description="Together AI API key")

    _required_credentials = {"together_api_key"}

    async def validate_credentials(self) -> bool:
        """Validate Together AI credentials"""
        try:
            together.api_key = self.together_api_key.get_secret_value()
            await together.Models.list()
            return True
        except Exception as e:
            raise CredentialValidationError(
                f"Invalid Together AI credentials: {str(e)}"
            )
