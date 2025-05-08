from typing import Any, Dict, Generator, List, Optional, Type, TypeVar
from pydantic import BaseModel, Field
import requests
import json

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import FireworksCredentials

ResponseT = TypeVar("ResponseT")


class FireworksStructuredCompletionInput(InputSchema):
    """Schema for Fireworks AI structured completion input"""

    prompt: str = Field(..., description="Input prompt for completion")
    model: str = Field(
        default="accounts/fireworks/models/deepseek-r1",
        description="Fireworks AI model to use",
    )
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")
    response_model: Type[ResponseT]
    stream: bool = Field(
        default=False,
        description="Whether to stream the response token by token",
    )

    class Config:
        arbitrary_types_allowed = True


class FireworksStructuredCompletionOutput(OutputSchema):
    """Schema for Fireworks AI structured completion output"""

    parsed_response: Any
    used_model: str
    usage: Dict[str, int]
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description=(
            "Tool calls are not applicable for completions, "
            "included for compatibility"
        )
    )


class FireworksStructuredCompletionSkill(
    Skill[FireworksStructuredCompletionInput, FireworksStructuredCompletionOutput]
):
    """Skill for getting structured completion responses from Fireworks AI"""

    input_schema = FireworksStructuredCompletionInput
    output_schema = FireworksStructuredCompletionOutput
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

    def _build_payload(
        self, input_data: FireworksStructuredCompletionInput
    ) -> Dict[str, Any]:
        """Build the request payload."""
        return {
            "model": input_data.model,
            "prompt": input_data.prompt,
            "temperature": input_data.temperature,
            "max_tokens": input_data.max_tokens,
            "stream": input_data.stream,
            "response_format": {
                "type": "json_object",
                "schema": {
                    **input_data.response_model.model_json_schema(),
                    "required": [
                        field
                        for field, _ in input_data.response_model.model_fields.items()
                    ],
                },
            },
        }

    def process_stream(
        self, input_data: FireworksStructuredCompletionInput
    ) -> Generator[Dict[str, Any], None, None]:
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

            json_buffer = []
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8").removeprefix("data: "))
                        if data.get("choices") and data["choices"][0].get("text"):
                            content = data["choices"][0]["text"]
                            json_buffer.append(content)
                            yield {"chunk": content}
                    except json.JSONDecodeError:
                        continue

            # Once complete, parse the full JSON
            complete_json = "".join(json_buffer)
            try:
                parsed_response = input_data.response_model.model_validate_json(
                    complete_json
                )
                yield {"complete": parsed_response}
            except Exception as e:
                raise ProcessingError(f"Failed to parse JSON response: {str(e)}")

        except Exception as e:
            raise ProcessingError(f"Fireworks streaming request failed: {str(e)}")

    def process(
        self, input_data: FireworksStructuredCompletionInput
    ) -> FireworksStructuredCompletionOutput:
        """Process the input and return structured response."""
        try:
            if input_data.stream:
                # For streaming, collect and parse the entire response
                json_buffer = []
                parsed_response = None

                for chunk in self.process_stream(input_data):
                    if "chunk" in chunk:
                        json_buffer.append(chunk["chunk"])
                    elif "complete" in chunk:
                        parsed_response = chunk["complete"]

                if parsed_response is None:
                    raise ProcessingError("Failed to parse streamed response")

                return FireworksStructuredCompletionOutput(
                    parsed_response=parsed_response,
                    used_model=input_data.model,
                    usage={},  # Usage stats not available in streaming mode
                )
            else:
                # For non-streaming, use regular request
                payload = self._build_payload(input_data)
                response = requests.post(
                    self.BASE_URL, headers=self.headers, data=json.dumps(payload)
                )
                response.raise_for_status()
                data = response.json()

                response_text = data["choices"][0]["text"]

                response_text = response_text.split("</think>")[-1]

                parsed_response = input_data.response_model.model_validate_json(
                    response_text
                )

                return FireworksStructuredCompletionOutput(
                    parsed_response=parsed_response,
                    used_model=input_data.model,
                    usage=data["usage"],
                )

        except Exception as e:
            raise ProcessingError(f"Fireworks structured completion failed: {str(e)}")
