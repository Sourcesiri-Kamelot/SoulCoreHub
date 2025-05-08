from pydantic import Field, SecretStr
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
import requests


class PerplexityCredentials(BaseCredentials):
    """Perplexity AI API credentials"""

    perplexity_api_key: SecretStr = Field(..., description="Perplexity AI API key")

    _required_credentials = {"perplexity_api_key"}

    async def validate_credentials(self) -> bool:
        """Validate Perplexity AI credentials by making a test API call"""
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key.get_secret_value()}",
                "Content-Type": "application/json",
            }

            # Small API call to check if credentials are valid
            data = {
                "model": "sonar-pro",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 1,
            }

            # Make a synchronous request for validation
            response = requests.post(
                "https://api.perplexity.ai/chat/completions", headers=headers, json=data
            )

            if response.status_code == 200:
                return True
            else:
                raise CredentialValidationError(
                    f"Invalid Perplexity AI credentials: {response.status_code} - {response.text}"
                )

        except Exception as e:
            raise CredentialValidationError(
                f"Invalid Perplexity AI credentials: {str(e)}"
            )
