from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import FireworksCredentials
import re

# Generic type variable for Pydantic response models
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class FireworksParserInput(InputSchema):
    """Schema for Fireworks structured output input"""

    user_input: str
    system_prompt: str = "You are a helpful assistant that provides structured data."
    model: str = "accounts/fireworks/models/deepseek-r1"
    temperature: float = 0.7
    max_tokens: Optional[int] = 131072
    response_model: Type[ResponseT]
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of previous conversation messages in [{'role': 'user|assistant', 'content': 'message'}] format",
    )

    class Config:
        arbitrary_types_allowed = True


class FireworksParserOutput(OutputSchema):
    """Schema for Fireworks structured output"""

    parsed_response: BaseModel
    used_model: str
    tokens_used: int
    reasoning: Optional[str] = None


class FireworksParserSkill(Skill[FireworksParserInput, FireworksParserOutput]):
    """Skill for getting structured responses from Fireworks"""

    input_schema = FireworksParserInput
    output_schema = FireworksParserOutput

    def __init__(self, credentials: Optional[FireworksCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or FireworksCredentials.from_env()
        self.client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=self.credentials.fireworks_api_key.get_secret_value(),
        )

    def process(self, input_data: FireworksParserInput) -> FireworksParserOutput:
        try:
            # Build messages list including conversation history
            messages = [{"role": "system", "content": input_data.system_prompt}]

            # Add conversation history if present
            if input_data.conversation_history:
                messages.extend(input_data.conversation_history)

            # Add current user input
            messages.append({"role": "user", "content": input_data.user_input})

            # Make API call with JSON schema
            completion = self.client.chat.completions.create(
                model=input_data.model,
                messages=messages,
                response_format={
                    "type": "json_object",
                    "schema": input_data.response_model.model_json_schema(),
                },
                temperature=input_data.temperature,
                max_tokens=input_data.max_tokens,
            )

            response_content = completion.choices[0].message.content

            # Extract reasoning if present
            reasoning_match = re.search(
                r"<think>(.*?)</think>", response_content, re.DOTALL
            )
            reasoning = reasoning_match.group(1).strip() if reasoning_match else None

            # Extract JSON
            json_match = re.search(r"</think>\s*(\{.*\})", response_content, re.DOTALL)
            json_str = json_match.group(1).strip() if json_match else response_content

            # Parse the response into the specified model
            parsed_response = input_data.response_model.parse_raw(json_str)

            return FireworksParserOutput(
                parsed_response=parsed_response,
                used_model=completion.model,
                tokens_used=completion.usage.total_tokens,
                reasoning=reasoning,
            )

        except Exception as e:
            raise ProcessingError(f"Fireworks parsing failed: {str(e)}")
