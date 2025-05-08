from typing import Optional, Dict, Any, List
from pydantic import Field

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from airtrain.core.credentials import BaseCredentials

# Import existing list models skills
from airtrain.integrations.openai.list_models import OpenAIListModelsSkill
from airtrain.integrations.anthropic.list_models import AnthropicListModelsSkill
from airtrain.integrations.together.list_models import TogetherListModelsSkill
from airtrain.integrations.fireworks.list_models import FireworksListModelsSkill

# Import credentials
from airtrain.integrations.groq.credentials import GroqCredentials
from airtrain.integrations.cerebras.credentials import CerebrasCredentials
from airtrain.integrations.sambanova.credentials import SambanovaCredentials
from airtrain.integrations.perplexity.credentials import PerplexityCredentials

# Remove this import to avoid circular dependency
# from airtrain.integrations.perplexity.list_models import PerplexityListModelsSkill


# Generic list models input schema
class GenericListModelsInput(InputSchema):
    """Generic schema for listing models from any provider"""

    api_models_only: bool = Field(
        default=False,
        description=(
            "If True, fetch models from the API only. If False, use local config."
        ),
    )

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


# Generic list models output schema
class GenericListModelsOutput(OutputSchema):
    """Generic schema for list models output from any provider"""

    models: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of models"
    )
    provider: str = Field(..., description="Provider name")


# Base class for stub implementations
class BaseListModelsSkill(Skill[GenericListModelsInput, GenericListModelsOutput]):
    """Base skill for listing models"""

    input_schema = GenericListModelsInput
    output_schema = GenericListModelsOutput

    def __init__(self, provider: str, credentials: Optional[BaseCredentials] = None):
        """Initialize the skill with provider name and optional credentials"""
        super().__init__()
        self.provider = provider
        self.credentials = credentials

    def get_models(self) -> List[Dict[str, Any]]:
        """Return list of models. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_models()")

    def process(self, input_data: GenericListModelsInput) -> GenericListModelsOutput:
        """Process the input and return a list of models."""
        try:
            models = self.get_models()
            return GenericListModelsOutput(models=models, provider=self.provider)
        except Exception as e:
            raise ProcessingError(f"Failed to list {self.provider} models: {str(e)}")


# Groq implementation
class GroqListModelsSkill(BaseListModelsSkill):
    """Skill for listing Groq models"""

    def __init__(self, credentials: Optional[GroqCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__(provider="groq", credentials=credentials)

    def get_models(self) -> List[Dict[str, Any]]:
        """Return list of Groq models."""
        # Default Groq models from trmx_agent config
        models = [
            {
                "id": "llama-3.3-70b-versatile",
                "display_name": "Llama 3.3 70B Versatile (Tool Use)",
            },
            {
                "id": "llama-3.1-8b-instant",
                "display_name": "Llama 3.1 8B Instant (Tool Use)",
            },
            {
                "id": "mixtral-8x7b-32768",
                "display_name": "Mixtral 8x7B (32K) (Tool Use)",
            },
            {"id": "gemma2-9b-it", "display_name": "Gemma 2 9B IT (Tool Use)"},
            {"id": "qwen-qwq-32b", "display_name": "Qwen QWQ 32B (Tool Use)"},
            {
                "id": "qwen-2.5-coder-32b",
                "display_name": "Qwen 2.5 Coder 32B (Tool Use)",
            },
            {"id": "qwen-2.5-32b", "display_name": "Qwen 2.5 32B (Tool Use)"},
            {
                "id": "deepseek-r1-distill-qwen-32b",
                "display_name": "DeepSeek R1 Distill Qwen 32B (Tool Use)",
            },
            {
                "id": "deepseek-r1-distill-llama-70b",
                "display_name": "DeepSeek R1 Distill Llama 70B (Tool Use)",
            },
        ]
        return models


# Cerebras implementation
class CerebrasListModelsSkill(BaseListModelsSkill):
    """Skill for listing Cerebras models"""

    def __init__(self, credentials: Optional[CerebrasCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__(provider="cerebras", credentials=credentials)

    def get_models(self) -> List[Dict[str, Any]]:
        """Return list of Cerebras models."""
        # Default Cerebras models from trmx_agent config
        models = [
            {
                "id": "cerebras/Cerebras-GPT-13B-v0.1",
                "display_name": "Cerebras GPT 13B v0.1",
            },
            {
                "id": "cerebras/Cerebras-GPT-111M-v0.9",
                "display_name": "Cerebras GPT 111M v0.9",
            },
            {
                "id": "cerebras/Cerebras-GPT-590M-v0.7",
                "display_name": "Cerebras GPT 590M v0.7",
            },
        ]
        return models


# Sambanova implementation
class SambanovaListModelsSkill(BaseListModelsSkill):
    """Skill for listing Sambanova models"""

    def __init__(self, credentials: Optional[SambanovaCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__(provider="sambanova", credentials=credentials)

    def get_models(self) -> List[Dict[str, Any]]:
        """Return list of Sambanova models."""
        # Limited Sambanova model information
        models = [
            {"id": "sambanova/samba-1", "display_name": "Samba-1"},
            {"id": "sambanova/samba-2", "display_name": "Samba-2"},
        ]
        return models


# Factory class
class ListModelsSkillFactory:
    """Factory for creating list models skills for different providers"""

    # Map provider names to their corresponding list models skills
    _PROVIDER_MAP = {
        "openai": OpenAIListModelsSkill,
        "anthropic": AnthropicListModelsSkill,
        "together": TogetherListModelsSkill,
        "fireworks": FireworksListModelsSkill,
        "groq": GroqListModelsSkill,
        "cerebras": CerebrasListModelsSkill,
        "sambanova": SambanovaListModelsSkill,
        # Remove perplexity from this map as we'll handle it separately
        # "perplexity": PerplexityListModelsSkill,
    }

    @classmethod
    def get_skill(cls, provider: str, credentials=None):
        """Return a list models skill for the specified provider

        Args:
            provider (str): The provider name (case-insensitive)
            credentials: Optional credentials for the provider

        Returns:
            A ListModelsSkill instance for the specified provider

        Raises:
            ValueError: If the provider is not supported
        """
        provider = provider.lower()

        # Special case for perplexity to avoid circular import
        if provider == "perplexity":
            # Import here to avoid circular import
            from airtrain.integrations.perplexity.list_models import (
                PerplexityListModelsSkill,
            )

            return PerplexityListModelsSkill(credentials=credentials)

        if provider not in cls._PROVIDER_MAP:
            supported = ", ".join(cls.get_supported_providers() + ["perplexity"])
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers are: {supported}"
            )

        skill_class = cls._PROVIDER_MAP[provider]
        return skill_class(credentials=credentials)

    @classmethod
    def get_supported_providers(cls):
        """Return a list of supported provider names"""
        # Add perplexity to the list of supported providers
        return list(cls._PROVIDER_MAP.keys()) + ["perplexity"]
