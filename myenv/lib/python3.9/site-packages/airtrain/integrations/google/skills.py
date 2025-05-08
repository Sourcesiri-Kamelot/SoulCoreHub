from typing import List, Optional, Dict, Any
from pydantic import Field
import google.generativeai as genai
from loguru import logger

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import GeminiCredentials


class GoogleGenerationConfig(InputSchema):
    """Schema for Google generation config"""

    temperature: float = Field(
        default=1.0, description="Temperature for response generation", ge=0, le=1
    )
    top_p: float = Field(
        default=0.95, description="Top p sampling parameter", ge=0, le=1
    )
    top_k: int = Field(default=40, description="Top k sampling parameter")
    max_output_tokens: int = Field(
        default=8192, description="Maximum tokens in response"
    )
    response_mime_type: str = Field(
        default="text/plain", description="Response MIME type"
    )


class GoogleInput(InputSchema):
    """Schema for Google chat input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    conversation_history: List[Dict[str, str | List[Dict[str, str]]]] = Field(
        default_factory=list,
        description="List of conversation messages in Google's format",
    )
    model: str = Field(default="gemini-1.5-flash", description="Google model to use")
    generation_config: GoogleGenerationConfig = Field(
        default_factory=GoogleGenerationConfig, description="Generation configuration"
    )


class GoogleOutput(OutputSchema):
    """Schema for Google chat output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")


class GoogleChatSkill(Skill[GoogleInput, GoogleOutput]):
    """Skill for Google chat"""

    input_schema = GoogleInput
    output_schema = GoogleOutput

    def __init__(self, credentials: Optional[GeminiCredentials] = None):
        super().__init__()
        self.credentials = credentials or GeminiCredentials.from_env()
        genai.configure(api_key=self.credentials.gemini_api_key.get_secret_value())

    def _convert_history_format(
        self, history: List[Dict[str, str]]
    ) -> List[Dict[str, List[Dict[str, str]]]]:
        """Convert standard history format to Google's format"""
        google_history = []
        for msg in history:
            google_msg = {
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}],
            }
            google_history.append(google_msg)
        return google_history

    def process(self, input_data: GoogleInput) -> GoogleOutput:
        try:
            # Create generation config
            generation_config = {
                "temperature": input_data.generation_config.temperature,
                "top_p": input_data.generation_config.top_p,
                "top_k": input_data.generation_config.top_k,
                "max_output_tokens": input_data.generation_config.max_output_tokens,
                "response_mime_type": input_data.generation_config.response_mime_type,
            }

            # Initialize model
            model = genai.GenerativeModel(
                model_name=input_data.model,
                generation_config=generation_config,
                system_instruction=input_data.system_prompt,
            )

            # Convert history format if needed
            history = (
                input_data.conversation_history
                if input_data.conversation_history
                else self._convert_history_format([])
            )

            # Start chat session
            chat = model.start_chat(history=history)

            # Send message and get response
            response = chat.send_message(input_data.user_input)

            return GoogleOutput(
                response=response.text,
                used_model=input_data.model,
                usage={
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },  # Google API doesn't provide usage stats
            )

        except Exception as e:
            logger.exception(f"Google processing failed: {str(e)}")
            raise ProcessingError(f"Google processing failed: {str(e)}")
