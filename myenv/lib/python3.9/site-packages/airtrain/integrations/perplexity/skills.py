from typing import Dict, Any, List, Optional, Generator, Union
from pydantic import Field, validator
import requests

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import PerplexityCredentials
from .models_config import get_model_config, get_default_model


class PerplexityInput(InputSchema):
    """Schema for Perplexity AI chat input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: Optional[str] = Field(
        default=None,
        description="System prompt to guide the model's behavior",
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of previous conversation messages in [{'role': 'user|assistant', 'content': 'message'}] format",
    )
    model: str = Field(
        default="sonar-pro",
        description="Perplexity AI model to use",
    )
    temperature: Optional[float] = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    max_tokens: Optional[int] = Field(
        default=500, description="Maximum tokens in response"
    )
    top_p: Optional[float] = Field(
        default=1.0, description="Top-p (nucleus) sampling parameter", ge=0, le=1
    )
    top_k: Optional[int] = Field(
        default=None,
        description="Top-k sampling parameter",
    )
    presence_penalty: Optional[float] = Field(
        default=None,
        description="Presence penalty parameter",
    )
    frequency_penalty: Optional[float] = Field(
        default=None,
        description="Frequency penalty parameter",
    )

    @validator("model")
    def validate_model(cls, v):
        """Validate that the model is supported by Perplexity AI."""
        try:
            get_model_config(v)
            return v
        except ValueError as e:
            raise ValueError(f"Invalid Perplexity AI model: {v}. {str(e)}")


class PerplexityCitation(OutputSchema):
    """Schema for Perplexity AI citation information"""

    url: str = Field(..., description="URL of the citation source")
    title: Optional[str] = Field(None, description="Title of the cited source")
    snippet: Optional[str] = Field(None, description="Text snippet from the citation")


class PerplexityOutput(OutputSchema):
    """Schema for Perplexity AI chat output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, int] = Field(..., description="Usage statistics from the API")
    citations: Optional[List[PerplexityCitation]] = Field(
        default=None, description="Citations used in the response, if available"
    )
    search_queries: Optional[List[str]] = Field(
        default=None, description="Search queries used, if available"
    )


class PerplexityChatSkill(Skill[PerplexityInput, PerplexityOutput]):
    """Skill for interacting with Perplexity AI models"""

    input_schema = PerplexityInput
    output_schema = PerplexityOutput

    def __init__(self, credentials: Optional[PerplexityCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or PerplexityCredentials.from_env()
        self.api_url = "https://api.perplexity.ai/chat/completions"

    def _build_messages(self, input_data: PerplexityInput) -> List[Dict[str, str]]:
        """Build messages list from input data including conversation history."""
        messages = []

        # Add system prompt if provided
        if input_data.system_prompt:
            messages.append({"role": "system", "content": input_data.system_prompt})

        # Add conversation history
        if input_data.conversation_history:
            messages.extend(input_data.conversation_history)

        # Add current user input
        messages.append({"role": "user", "content": input_data.user_input})

        return messages

    def _prepare_api_parameters(self, input_data: PerplexityInput) -> Dict[str, Any]:
        """Prepare parameters for the API request."""
        parameters = {
            "model": input_data.model,
            "messages": self._build_messages(input_data),
            "max_tokens": input_data.max_tokens,
        }

        # Add optional parameters if provided
        if input_data.temperature is not None:
            parameters["temperature"] = input_data.temperature

        if input_data.top_p is not None:
            parameters["top_p"] = input_data.top_p

        if input_data.top_k is not None:
            parameters["top_k"] = input_data.top_k

        if input_data.presence_penalty is not None:
            parameters["presence_penalty"] = input_data.presence_penalty

        if input_data.frequency_penalty is not None:
            parameters["frequency_penalty"] = input_data.frequency_penalty

        return parameters

    def process(self, input_data: PerplexityInput) -> PerplexityOutput:
        """Process the input and return the complete response."""
        try:
            # Prepare headers with API key
            headers = {
                "Authorization": f"Bearer {self.credentials.perplexity_api_key.get_secret_value()}",
                "Content-Type": "application/json",
            }

            # Prepare parameters for the API request
            data = self._prepare_api_parameters(input_data)

            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data)

            # Check if request was successful
            if response.status_code != 200:
                raise ProcessingError(
                    f"Perplexity AI API error: {response.status_code} - {response.text}"
                )

            # Parse the response
            result = response.json()

            # Extract content from the completion
            content = result["choices"][0]["message"]["content"]

            # Extract and process citations if available
            citations = None
            if "citations" in result:
                citations = [
                    PerplexityCitation(
                        url=citation.get("url", ""),
                        title=citation.get("title"),
                        snippet=citation.get("snippet"),
                    )
                    for citation in result.get("citations", [])
                ]

            # Extract search queries if available
            search_queries = None
            if "usage" in result and "num_search_queries" in result["usage"]:
                search_queries = result.get("search_queries", [])

            # Create and return output
            return PerplexityOutput(
                response=content,
                used_model=input_data.model,
                usage=result.get("usage", {}),
                citations=citations,
                search_queries=search_queries,
            )

        except Exception as e:
            if isinstance(e, ProcessingError):
                raise e
            raise ProcessingError(f"Perplexity AI processing failed: {str(e)}")


class PerplexityProcessStreamError(Exception):
    """Error raised during stream processing"""

    pass


class PerplexityStreamOutput(OutputSchema):
    """Schema for streaming output tokens"""

    token: str = Field(..., description="Text token")
    finish_reason: Optional[str] = Field(
        None, description="Why the completion finished"
    )


class PerplexityStreamingChatSkill(PerplexityChatSkill):
    """Extension of PerplexityChatSkill that supports streaming responses"""

    def process_stream(
        self, input_data: PerplexityInput
    ) -> Generator[PerplexityStreamOutput, None, None]:
        """
        Process the input and stream the response tokens.

        Note: Perplexity AI API may not support true streaming. In that case, this
        method will make a regular API call and yield the entire response at once.
        """
        try:
            # Prepare headers with API key
            headers = {
                "Authorization": f"Bearer {self.credentials.perplexity_api_key.get_secret_value()}",
                "Content-Type": "application/json",
            }

            # Prepare parameters for the API request, including stream=true if possible
            data = self._prepare_api_parameters(input_data)
            data["stream"] = True

            # Make the API request
            response = requests.post(
                self.api_url, headers=headers, json=data, stream=True
            )

            # Check if request was successful
            if response.status_code != 200:
                raise PerplexityProcessStreamError(
                    f"Perplexity AI API error: {response.status_code} - {response.text}"
                )

            # Process the streaming response if supported
            for line in response.iter_lines():
                if line:
                    # Parse the response line
                    try:
                        # Remove 'data: ' prefix if present
                        if line.startswith(b"data: "):
                            line = line[6:]

                        # Parse JSON
                        import json

                        chunk = json.loads(line)

                        # Extract content
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            choice = chunk["choices"][0]
                            if "delta" in choice and "content" in choice["delta"]:
                                content = choice["delta"]["content"]
                                if content:
                                    yield PerplexityStreamOutput(
                                        token=content,
                                        finish_reason=choice.get("finish_reason"),
                                    )
                    except json.JSONDecodeError:
                        # Skip non-JSON lines
                        continue
                    except Exception as e:
                        raise PerplexityProcessStreamError(
                            f"Error processing stream chunk: {str(e)}"
                        )

        except Exception as e:
            if isinstance(e, PerplexityProcessStreamError):
                raise ProcessingError(str(e))
            raise ProcessingError(f"Perplexity AI streaming failed: {str(e)}")
