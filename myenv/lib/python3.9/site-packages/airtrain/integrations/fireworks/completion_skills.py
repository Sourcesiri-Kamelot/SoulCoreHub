from typing import List, Optional, Dict, Any, Generator, Union
from pydantic import Field
import requests
import json
from loguru import logger

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import FireworksCredentials


class FireworksCompletionInput(InputSchema):
    """Schema for Fireworks AI completion input using requests"""

    prompt: str = Field(..., description="Input prompt for completion")
    model: str = Field(
        default="accounts/fireworks/models/deepseek-r1",
        description="Fireworks AI model to use",
    )
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    top_p: float = Field(
        default=1.0, description="Top p sampling parameter", ge=0, le=1
    )
    top_k: int = Field(default=50, description="Top k sampling parameter", ge=0)
    presence_penalty: float = Field(
        default=0.0, description="Presence penalty", ge=-2.0, le=2.0
    )
    frequency_penalty: float = Field(
        default=0.0, description="Frequency penalty", ge=-2.0, le=2.0
    )
    repetition_penalty: float = Field(
        default=1.0, description="Repetition penalty", ge=0.0
    )
    stop: Optional[Union[str, List[str]]] = Field(
        default=None, description="Stop sequences"
    )
    echo: bool = Field(default=False, description="Echo the prompt in the response")
    stream: bool = Field(default=False, description="Whether to stream the response")


class FireworksCompletionOutput(OutputSchema):
    """Schema for Fireworks AI completion output"""

    response: str
    used_model: str
    usage: Dict[str, int]


class FireworksCompletionSkill(
    Skill[FireworksCompletionInput, FireworksCompletionOutput]
):
    """Skill for text completion using Fireworks AI"""

    input_schema = FireworksCompletionInput
    output_schema = FireworksCompletionOutput
    BASE_URL = "https://api.fireworks.ai/inference/v1/completions"

    def __init__(self, credentials: Optional[FireworksCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or FireworksCredentials.from_env()
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.credentials.fireworks_api_key.get_secret_value()}",
        }

    def _build_payload(self, input_data: FireworksCompletionInput) -> Dict[str, Any]:
        """Build the request payload."""
        payload = {
            "model": input_data.model,
            "prompt": input_data.prompt,
            "max_tokens": input_data.max_tokens,
            "temperature": input_data.temperature,
            "top_p": input_data.top_p,
            "top_k": input_data.top_k,
            "presence_penalty": input_data.presence_penalty,
            "frequency_penalty": input_data.frequency_penalty,
            "repetition_penalty": input_data.repetition_penalty,
            "echo": input_data.echo,
            "stream": input_data.stream,
        }

        if input_data.stop:
            payload["stop"] = input_data.stop

        return payload

    def process_stream(
        self, input_data: FireworksCompletionInput
    ) -> Generator[str, None, None]:
        """Process the input and stream the response."""
        try:
            payload = self._build_payload(input_data)
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                data=json.dumps(payload),
                stream=True,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8").removeprefix("data: "))
                        if data.get("choices") and data["choices"][0].get("text"):
                            yield data["choices"][0]["text"]
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            raise ProcessingError(f"Fireworks completion streaming failed: {str(e)}")

    def process(
        self, input_data: FireworksCompletionInput
    ) -> FireworksCompletionOutput:
        """Process the input and return completion response."""
        try:
            if input_data.stream:
                # For streaming, collect the entire response
                response_chunks = []
                for chunk in self.process_stream(input_data):
                    response_chunks.append(chunk)
                response_text = "".join(response_chunks)
                usage = {}  # Usage stats not available in streaming mode
            else:
                # For non-streaming, use regular request
                payload = self._build_payload(input_data)
                response = requests.post(
                    self.BASE_URL, headers=self.headers, data=json.dumps(payload)
                )
                response.raise_for_status()
                data = response.json()

                response_text = data["choices"][0]["text"]
                usage = data["usage"]

            return FireworksCompletionOutput(
                response=response_text, used_model=input_data.model, usage=usage
            )

        except Exception as e:
            raise ProcessingError(f"Fireworks completion failed: {str(e)}")
