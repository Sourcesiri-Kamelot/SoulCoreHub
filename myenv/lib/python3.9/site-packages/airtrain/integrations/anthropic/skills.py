from typing import List, Optional, Dict, Any, Generator
from pydantic import Field
from anthropic import Anthropic
import base64
from pathlib import Path
from loguru import logger

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import AnthropicCredentials


class AnthropicInput(InputSchema):
    """Schema for Anthropic chat input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of previous conversation messages in [{'role': 'user|assistant', 'content': 'message'}] format",
    )
    model: str = Field(
        default="claude-3-opus-20240229", description="Anthropic model to use"
    )
    max_tokens: Optional[int] = Field(
        default=131072, description="Maximum tokens in response"
    )
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    images: List[Path] = Field(
        default_factory=list,
        description="List of image paths to include in the message",
    )
    stream: bool = Field(
        default=False, description="Whether to stream the response progressively"
    )


class AnthropicOutput(OutputSchema):
    """Schema for Anthropic chat output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(
        default_factory=dict, description="Usage statistics from the API"
    )


class AnthropicChatSkill(Skill[AnthropicInput, AnthropicOutput]):
    """Skill for Anthropic chat"""

    input_schema = AnthropicInput
    output_schema = AnthropicOutput

    def __init__(self, credentials: Optional[AnthropicCredentials] = None):
        super().__init__()
        self.credentials = credentials or AnthropicCredentials.from_env()
        self.client = Anthropic(
            api_key=self.credentials.anthropic_api_key.get_secret_value()
        )

    def _build_messages(self, input_data: AnthropicInput) -> List[Dict[str, Any]]:
        """
        Build messages list from input data including conversation history.

        Args:
            input_data: The input data containing system prompt, conversation history, and user input

        Returns:
            List[Dict[str, Any]]: List of messages in the format required by Anthropic
        """
        messages = []

        # Add conversation history if present
        if input_data.conversation_history:
            messages.extend(input_data.conversation_history)

        # Prepare user message content
        user_message = {"type": "text", "text": input_data.user_input}

        # Add images if present
        if input_data.images:
            content = []
            for image_path in input_data.images:
                with open(image_path, "rb") as img_file:
                    base64_image = base64.b64encode(img_file.read()).decode("utf-8")
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image,
                        },
                    }
                )
            content.append(user_message)
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": [user_message]})

        return messages

    def process_stream(self, input_data: AnthropicInput) -> Generator[str, None, None]:
        """Process the input and stream the response token by token."""
        try:
            messages = self._build_messages(input_data)

            with self.client.beta.messages.stream(
                model=input_data.model,
                system=input_data.system_prompt,
                messages=messages,
                max_tokens=input_data.max_tokens,
                temperature=input_data.temperature,
            ) as stream:
                for chunk in stream.text_stream:
                    yield chunk

        except Exception as e:
            logger.exception(f"Anthropic streaming failed: {str(e)}")
            raise ProcessingError(f"Anthropic streaming failed: {str(e)}")

    def process(self, input_data: AnthropicInput) -> AnthropicOutput:
        """Process the input and return the complete response."""
        try:
            if input_data.stream:
                response_chunks = []
                for chunk in self.process_stream(input_data):
                    response_chunks.append(chunk)
                response = "".join(response_chunks)
                usage = {}  # Usage stats not available in streaming
            else:
                messages = self._build_messages(input_data)
                response = self.client.messages.create(
                    model=input_data.model,
                    system=input_data.system_prompt,
                    messages=messages,
                    max_tokens=input_data.max_tokens,
                    temperature=input_data.temperature,
                )
                usage = response.usage.model_dump() if response.usage else {}

            return AnthropicOutput(
                response=response.content[0].text,
                used_model=input_data.model,
                usage=usage,
            )

        except Exception as e:
            logger.exception(f"Anthropic processing failed: {str(e)}")
            raise ProcessingError(f"Anthropic processing failed: {str(e)}")
