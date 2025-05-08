from typing import Optional
from pydantic import Field, SecretStr
from airtrain.core.credentials import BaseCredentials, CredentialValidationError
import boto3


class AWSCredentials(BaseCredentials):
    """AWS credentials"""

    aws_access_key_id: SecretStr = Field(..., description="AWS Access Key ID")
    aws_secret_access_key: SecretStr = Field(..., description="AWS Secret Access Key")
    aws_region: str = Field(default="us-east-1", description="AWS Region")
    aws_session_token: Optional[SecretStr] = Field(
        None, description="AWS Session Token"
    )

    _required_credentials = {"aws_access_key_id", "aws_secret_access_key"}

    async def validate_credentials(self) -> bool:
        """Validate AWS credentials by making a test API call"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id.get_secret_value(),
                aws_secret_access_key=self.aws_secret_access_key.get_secret_value(),
                aws_session_token=(
                    self.aws_session_token.get_secret_value()
                    if self.aws_session_token
                    else None
                ),
                region_name=self.aws_region,
            )
            sts = session.client("sts")
            sts.get_caller_identity()
            return True
        except Exception as e:
            raise CredentialValidationError(f"Invalid AWS credentials: {str(e)}")
