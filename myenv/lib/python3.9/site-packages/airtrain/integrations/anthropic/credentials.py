from pydantic import Field, SecretStr, validator
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
from anthropic import Anthropic


class AnthropicCredentials(BaseCredentials):
    """Anthropic API credentials"""

    anthropic_api_key: SecretStr = Field(..., description="Anthropic API key")
    version: str = Field(default="2023-06-01", description="API Version")

    _required_credentials = {"anthropic_api_key"}

    @validator("anthropic_api_key")
    def validate_api_key_format(cls, v: SecretStr) -> SecretStr:
        key = v.get_secret_value()
        if not key.startswith("sk-ant-"):
            raise ValueError("Anthropic API key must start with 'sk-ant-'")
        return v

    async def validate_credentials(self) -> bool:
        """Validate Anthropic credentials"""
        try:
            client = Anthropic(api_key=self.anthropic_api_key.get_secret_value())
            client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid Anthropic credentials: {str(e)}")
