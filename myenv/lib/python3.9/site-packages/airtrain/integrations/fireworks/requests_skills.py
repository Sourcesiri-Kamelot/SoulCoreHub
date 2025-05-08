from typing import List, Optional, Dict, Any, Generator, AsyncGenerator
from pydantic import Field
import requests
import json
from loguru import logger
import aiohttp

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import FireworksCredentials


class FireworksRequestInput(InputSchema):
    """Schema for Fireworks AI chat input using requests"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of previous conversation messages",
    )
    model: str = Field(
        default="accounts/fireworks/models/deepseek-r1",
        description="Fireworks AI model to use",
    )
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")
    top_p: float = Field(
        default=1.0, description="Top p sampling parameter", ge=0, le=1
    )
    top_k: int = Field(default=40, description="Top k sampling parameter", ge=0)
    presence_penalty: float = Field(
        default=0.0, description="Presence penalty", ge=-2.0, le=2.0
    )
    frequency_penalty: float = Field(
        default=0.0, description="Frequency penalty", ge=-2.0, le=2.0
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response",
    )


class FireworksRequestOutput(OutputSchema):
    """Schema for Fireworks AI chat output"""

    response: str
    used_model: str
    usage: Dict[str, int]


class FireworksRequestSkill(Skill[FireworksRequestInput, FireworksRequestOutput]):
    """Skill for interacting with Fireworks AI models using requests"""

    input_schema = FireworksRequestInput
    output_schema = FireworksRequestOutput
    BASE_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

    def __init__(self, credentials: Optional[FireworksCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or FireworksCredentials.from_env()
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.credentials.fireworks_api_key.get_secret_value()}",
        }
        self.stream_headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.credentials.fireworks_api_key.get_secret_value()}",
        }

    def _build_messages(
        self, input_data: FireworksRequestInput
    ) -> List[Dict[str, str]]:
        """Build messages list from input data including conversation history."""
        messages = [{"role": "system", "content": input_data.system_prompt}]

        if input_data.conversation_history:
            messages.extend(input_data.conversation_history)

        messages.append({"role": "user", "content": input_data.user_input})
        return messages

    def _build_payload(self, input_data: FireworksRequestInput) -> Dict[str, Any]:
        """Build the request payload."""
        return {
            "model": input_data.model,
            "messages": self._build_messages(input_data),
            "temperature": input_data.temperature,
            "max_tokens": input_data.max_tokens,
            "top_p": input_data.top_p,
            "top_k": input_data.top_k,
            "presence_penalty": input_data.presence_penalty,
            "frequency_penalty": input_data.frequency_penalty,
            "stream": input_data.stream,
        }

    def process_stream(
        self, input_data: FireworksRequestInput
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
                        if data["choices"][0]["delta"].get("content"):
                            yield data["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            raise ProcessingError(f"Fireworks streaming request failed: {str(e)}")

    def process(self, input_data: FireworksRequestInput) -> FireworksRequestOutput:
        """Process the input and return the complete response."""
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

                response_text = data["choices"][0]["message"]["content"]
                usage = data["usage"]

            return FireworksRequestOutput(
                response=response_text, used_model=input_data.model, usage=usage
            )

        except Exception as e:
            raise ProcessingError(f"Fireworks request failed: {str(e)}")

    async def process_async(
        self, input_data: FireworksRequestInput
    ) -> FireworksRequestOutput:
        """Async version of process method using aiohttp"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = self._build_payload(input_data)
                async with session.post(
                    self.BASE_URL, headers=self.headers, json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    return FireworksRequestOutput(
                        response=data["choices"][0]["message"]["content"],
                        used_model=input_data.model,
                        usage=data.get("usage", {}),
                    )

        except Exception as e:
            raise ProcessingError(f"Async Fireworks request failed: {str(e)}")

    async def process_stream_async(
        self, input_data: FireworksRequestInput
    ) -> AsyncGenerator[str, None]:
        """Async version of stream processor using aiohttp"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = self._build_payload(input_data)
                async with session.post(
                    self.BASE_URL, headers=self.stream_headers, json=payload
                ) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        if line.startswith(b"data: "):
                            chunk = json.loads(line[6:].strip())
                            if "choices" in chunk:
                                content = (
                                    chunk["choices"][0]
                                    .get("delta", {})
                                    .get("content", "")
                                )
                                if content:
                                    yield content

        except Exception as e:
            raise ProcessingError(f"Async Fireworks streaming failed: {str(e)}")
