from pydantic import Field, SecretStr
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
from groq import Groq


class GroqCredentials(BaseCredentials):
    """Groq API credentials"""

    groq_api_key: SecretStr = Field(..., description="Groq API key")

    _required_credentials = {"groq_api_key"}

    async def validate_credentials(self) -> bool:
        """Validate Groq credentials"""
        try:
            client = Groq(api_key=self.groq_api_key.get_secret_value())
            await client.chat.completions.create(
                messages=[{"role": "user", "content": "Hi"}],
                model="mixtral-8x7b-32768",
                max_tokens=1,
            )
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid Groq credentials: {str(e)}")
