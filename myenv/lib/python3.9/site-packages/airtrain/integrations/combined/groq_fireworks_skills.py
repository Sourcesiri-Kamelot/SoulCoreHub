from typing import Optional, Dict, Any, List
from pydantic import Field
import requests
from groq import Groq

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from airtrain.integrations.fireworks.completion_skills import (
    FireworksCompletionSkill,
    FireworksCompletionInput,
)


class GroqFireworksInput(InputSchema):
    """Schema for combined Groq and Fireworks input"""

    user_input: str = Field(..., description="User's input text")
    groq_model: str = Field(
        default="mixtral-8x7b-32768", description="Groq model to use"
    )
    fireworks_model: str = Field(
        default="accounts/fireworks/models/deepseek-r1",
        description="Fireworks model to use",
    )
    temperature: float = Field(
        default=0.7, description="Temperature for response generation"
    )
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")


class GroqFireworksOutput(OutputSchema):
    """Schema for combined Groq and Fireworks output"""

    combined_response: str
    groq_response: str
    fireworks_response: str
    used_models: Dict[str, str]
    usage: Dict[str, Dict[str, int]]


class GroqFireworksSkill(Skill[GroqFireworksInput, GroqFireworksOutput]):
    """Skill combining Groq and Fireworks responses"""

    input_schema = GroqFireworksInput
    output_schema = GroqFireworksOutput

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        fireworks_skill: Optional[FireworksCompletionSkill] = None,
    ):
        """Initialize the skill with optional API keys"""
        super().__init__()
        self.groq_client = Groq(api_key=groq_api_key)
        self.fireworks_skill = fireworks_skill or FireworksCompletionSkill()

    def _get_groq_response(self, input_data: GroqFireworksInput) -> Dict[str, Any]:
        """Get response from Groq"""
        try:
            completion = self.groq_client.chat.completions.create(
                model=input_data.groq_model,
                messages=[{"role": "user", "content": input_data.user_input}],
                temperature=input_data.temperature,
                max_tokens=input_data.max_tokens,
            )
            return {
                "response": completion.choices[0].message.content,
                "usage": completion.usage.model_dump(),
            }
        except Exception as e:
            raise ProcessingError(f"Groq request failed: {str(e)}")

    def _get_fireworks_response(
        self, groq_response: str, input_data: GroqFireworksInput
    ) -> Dict[str, Any]:
        """Get response from Fireworks"""
        try:
            formatted_prompt = (
                f"<USER>{input_data.user_input}</USER>\n<ASSISTANT>{groq_response}"
            )

            fireworks_input = FireworksCompletionInput(
                prompt=formatted_prompt,
                model=input_data.fireworks_model,
                temperature=input_data.temperature,
                max_tokens=input_data.max_tokens,
            )

            result = self.fireworks_skill.process(fireworks_input)
            return {"response": result.response, "usage": result.usage}
        except Exception as e:
            raise ProcessingError(f"Fireworks request failed: {str(e)}")

    def process(self, input_data: GroqFireworksInput) -> GroqFireworksOutput:
        """Process the input using both Groq and Fireworks"""
        try:
            # Get Groq response
            groq_result = self._get_groq_response(input_data)

            # Get Fireworks response
            fireworks_result = self._get_fireworks_response(
                groq_result["response"], input_data
            )

            # Combine responses in the required format
            combined_response = (
                f"<USER>{input_data.user_input}</USER>\n"
                f"<ASSISTANT>{groq_result['response']} {fireworks_result['response']}"
            )

            return GroqFireworksOutput(
                combined_response=combined_response,
                groq_response=groq_result["response"],
                fireworks_response=fireworks_result["response"],
                used_models={
                    "groq": input_data.groq_model,
                    "fireworks": input_data.fireworks_model,
                },
                usage={
                    "groq": groq_result["usage"],
                    "fireworks": fireworks_result["usage"],
                },
            )

        except Exception as e:
            raise ProcessingError(f"Combined processing failed: {str(e)}")
