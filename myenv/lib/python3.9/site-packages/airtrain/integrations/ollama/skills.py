from typing import Optional, Dict, Any
from pydantic import Field
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import OllamaCredentials


class OllamaInput(InputSchema):
    """Schema for Ollama input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    model: str = Field(default="llama2", description="Ollama model to use")
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )


class OllamaOutput(OutputSchema):
    """Schema for Ollama output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")


class OllamaChatSkill(Skill[OllamaInput, OllamaOutput]):
    """Skill for Ollama - Not Implemented"""

    input_schema = OllamaInput
    output_schema = OllamaOutput

    def __init__(self, credentials: Optional[OllamaCredentials] = None):
        raise NotImplementedError("OllamaChatSkill is not implemented yet")

    def process(self, input_data: OllamaInput) -> OllamaOutput:
        raise NotImplementedError("OllamaChatSkill is not implemented yet")
