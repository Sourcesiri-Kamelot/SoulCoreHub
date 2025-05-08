from typing import Dict, Any, List, Optional
import requests

from airtrain.core.skills import Skill, ProcessingError
from airtrain.integrations.combined.list_models_factory import (
    BaseListModelsSkill,
    GenericListModelsInput,
    GenericListModelsOutput,
)
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import PerplexityCredentials
from .models_config import PERPLEXITY_MODELS_CONFIG


class PerplexityListModelsInput(InputSchema):
    """Schema for listing Perplexity AI models"""

    api_models_only: bool = False


class PerplexityListModelsOutput(OutputSchema):
    """Schema for Perplexity AI models listing output"""

    models: List[Dict[str, Any]]
    provider: str = "perplexity"


class PerplexityListModelsSkill(BaseListModelsSkill):
    """Skill for listing Perplexity AI models"""

    def __init__(self, credentials: Optional[PerplexityCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__(provider="perplexity", credentials=credentials)
        self.credentials = credentials

    def get_models(self) -> List[Dict[str, Any]]:
        """Return list of Perplexity AI models."""
        models = []

        # Add models from the configuration
        for model_id, config in PERPLEXITY_MODELS_CONFIG.items():
            models.append(
                {
                    "id": model_id,
                    "display_name": config["name"],
                    "description": config.get("description", ""),
                    "category": config.get("category", "unknown"),
                    "capabilities": {
                        "citations": config.get("citations", False),
                        "search": config.get("search", False),
                        "context_window": config.get("context_window", 8192),
                        "max_completion_tokens": config.get(
                            "max_completion_tokens", 4096
                        ),
                    },
                }
            )

        return models

    def process(self, input_data: GenericListModelsInput) -> GenericListModelsOutput:
        """Process the input and return a list of models."""
        try:
            models = self.get_models()
            return GenericListModelsOutput(models=models, provider="perplexity")
        except Exception as e:
            raise ProcessingError(f"Failed to list Perplexity AI models: {str(e)}")


# Standalone version directly using the Perplexity-specific schemas
class StandalonePerplexityListModelsSkill(
    Skill[PerplexityListModelsInput, PerplexityListModelsOutput]
):
    """Standalone skill for listing Perplexity AI models"""

    input_schema = PerplexityListModelsInput
    output_schema = PerplexityListModelsOutput

    def __init__(self, credentials: Optional[PerplexityCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials

    def process(
        self, input_data: PerplexityListModelsInput
    ) -> PerplexityListModelsOutput:
        """Process the input and return a list of models."""
        try:
            models = []

            # Add models from the configuration
            for model_id, config in PERPLEXITY_MODELS_CONFIG.items():
                models.append(
                    {
                        "id": model_id,
                        "display_name": config["name"],
                        "description": config.get("description", ""),
                        "category": config.get("category", "unknown"),
                        "capabilities": {
                            "citations": config.get("citations", False),
                            "search": config.get("search", False),
                            "context_window": config.get("context_window", 8192),
                            "max_completion_tokens": config.get(
                                "max_completion_tokens", 4096
                            ),
                        },
                    }
                )

            return PerplexityListModelsOutput(models=models, provider="perplexity")
        except Exception as e:
            raise ProcessingError(f"Failed to list Perplexity AI models: {str(e)}")
