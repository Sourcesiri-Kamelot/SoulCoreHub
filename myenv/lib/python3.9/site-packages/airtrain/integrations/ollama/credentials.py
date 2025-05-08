from pydantic import Field
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
from importlib.util import find_spec


class OllamaCredentials(BaseCredentials):
    """Ollama credentials"""

    host: str = Field(default="http://localhost:11434", description="Ollama host URL")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    async def validate_credentials(self) -> bool:
        """Validate Ollama credentials"""
        if find_spec("ollama") is None:
            raise CredentialValidationError(
                "Ollama package is not installed. Please install it using: pip install ollama"
            )

        try:
            from ollama import Client

            client = Client(host=self.host)
            await client.list()
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid Ollama connection: {str(e)}")
