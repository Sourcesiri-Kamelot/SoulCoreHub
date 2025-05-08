from pydantic import Field, SecretStr
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
import google.genai as genai
from google.cloud import storage
import os

# from google.cloud import storage


class GoogleCloudCredentials(BaseCredentials):
    """Google Cloud credentials"""

    project_id: str = Field(..., description="Google Cloud Project ID")
    service_account_key: SecretStr = Field(..., description="Service Account Key JSON")

    _required_credentials = {"project_id", "service_account_key"}

    async def validate_credentials(self) -> bool:
        """Validate Google Cloud credentials"""
        try:
            # Initialize with service account key
            storage_client = storage.Client.from_service_account_info(
                self.service_account_key.get_secret_value()
            )
            # Test API call
            storage_client.list_buckets(max_results=1)
            return True
        except Exception as e:
            raise CredentialValidationError(
                f"Invalid Google Cloud credentials: {str(e)}"
            )


class GeminiCredentials(BaseCredentials):
    """Gemini API credentials"""

    gemini_api_key: SecretStr = Field(..., description="Gemini API Key")

    _required_credentials = {"gemini_api_key"}

    @classmethod
    def from_env(cls) -> "GeminiCredentials":
        """Create credentials from environment variables"""
        return cls(gemini_api_key=SecretStr(os.environ.get("GEMINI_API_KEY", "")))

    async def validate_credentials(self) -> bool:
        """Validate Gemini API credentials"""
        try:
            # Configure Gemini with API key
            genai.configure(api_key=self.gemini_api_key.get_secret_value())

            # Test API call with a simple model
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content("test")

            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid Gemini credentials: {str(e)}")
