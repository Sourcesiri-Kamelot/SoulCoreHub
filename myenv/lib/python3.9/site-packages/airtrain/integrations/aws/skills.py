from typing import List, Optional, Dict, Any
from pydantic import Field
import boto3
from pathlib import Path
from loguru import logger

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import AWSCredentials


class AWSBedrockInput(InputSchema):
    """Schema for AWS Bedrock chat input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(
        default="anthropic.claude-3-sonnet-20240229-v1:0",
        description="AWS Bedrock model to use",
    )
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    images: Optional[List[Path]] = Field(
        default=None,
        description="Optional list of image paths to include in the message",
    )


class AWSBedrockOutput(OutputSchema):
    """Schema for AWS Bedrock chat output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(
        default_factory=dict, description="Usage statistics from the API"
    )


class AWSBedrockSkill(Skill[AWSBedrockInput, AWSBedrockOutput]):
    """Skill for interacting with AWS Bedrock models"""

    input_schema = AWSBedrockInput
    output_schema = AWSBedrockOutput

    def __init__(self, credentials: Optional[AWSCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or AWSCredentials.from_env()
        self.client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=self.credentials.aws_access_key_id.get_secret_value(),
            aws_secret_access_key=self.credentials.aws_secret_access_key.get_secret_value(),
            region_name=self.credentials.aws_region,
        )

    def process(self, input_data: AWSBedrockInput) -> AWSBedrockOutput:
        """Process the input using AWS Bedrock API"""
        try:
            logger.info(f"Processing request with model {input_data.model}")

            # Prepare request body based on model provider
            if "anthropic" in input_data.model:
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": input_data.max_tokens,
                    "temperature": input_data.temperature,
                    "system": input_data.system_prompt,
                    "messages": [{"role": "user", "content": input_data.user_input}],
                }
            else:
                raise ProcessingError(f"Unsupported model: {input_data.model}")

            response = self.client.invoke_model(
                modelId=input_data.model, body=request_body
            )

            # Parse response based on model provider
            if "anthropic" in input_data.model:
                response_data = response["body"]["completion"]
                usage = {
                    "input_tokens": response["body"]["usage"]["input_tokens"],
                    "output_tokens": response["body"]["usage"]["output_tokens"],
                }
            else:
                raise ProcessingError(f"Unsupported model response: {input_data.model}")

            return AWSBedrockOutput(
                response=response_data, used_model=input_data.model, usage=usage
            )

        except Exception as e:
            logger.exception(f"AWS Bedrock processing failed: {str(e)}")
            raise ProcessingError(f"AWS Bedrock processing failed: {str(e)}")
