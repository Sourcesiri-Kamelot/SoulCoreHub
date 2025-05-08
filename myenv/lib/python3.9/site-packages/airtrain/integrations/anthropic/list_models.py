from typing import Optional, List, Dict, Any
from pydantic import Field

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import AnthropicCredentials
from .models_config import ANTHROPIC_MODELS, AnthropicModelConfig


class AnthropicModel:
    """Class to represent an Anthropic model."""
    
    def __init__(self, model_id: str, config: AnthropicModelConfig):
        """Initialize the Anthropic model."""
        self.id = model_id
        self.display_name = config.display_name
        self.base_model = config.base_model
        self.input_price = config.input_price
        self.cached_write_price = config.cached_write_price
        self.cached_read_price = config.cached_read_price
        self.output_price = config.output_price
    
    def dict(self, exclude_none=False):
        """Convert the model to a dictionary."""
        result = {
            "id": self.id,
            "display_name": self.display_name,
            "base_model": self.base_model,
            "input_price": float(self.input_price),
            "output_price": float(self.output_price),
        }
        
        if self.cached_write_price is not None:
            result["cached_write_price"] = float(self.cached_write_price)
        elif not exclude_none:
            result["cached_write_price"] = None
            
        if self.cached_read_price is not None:
            result["cached_read_price"] = float(self.cached_read_price)
        elif not exclude_none:
            result["cached_read_price"] = None
            
        return result


class AnthropicListModelsInput(InputSchema):
    """Schema for Anthropic list models input"""
    
    api_models_only: bool = Field(
        default=False,
        description=(
            "If True, fetch models from the API only. If False, use local config."
        )
    )


class AnthropicListModelsOutput(OutputSchema):
    """Schema for Anthropic list models output"""
    
    models: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of Anthropic models"
    )


class AnthropicListModelsSkill(
    Skill[AnthropicListModelsInput, AnthropicListModelsOutput]
):
    """Skill for listing Anthropic models"""

    input_schema = AnthropicListModelsInput
    output_schema = AnthropicListModelsOutput
    
    def __init__(self, credentials: Optional[AnthropicCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials
    
    def process(
        self, input_data: AnthropicListModelsInput
    ) -> AnthropicListModelsOutput:
        """Process the input and return a list of models."""
        try:
            models = []
            
            if input_data.api_models_only:
                # Fetch models from Anthropic API
                # Require credentials if using API models
                if not self.credentials:
                    raise ProcessingError(
                        "Anthropic credentials required for API models"
                    )
                
                # Note: Anthropic doesn't have a public models list endpoint
                # We'll raise an error instead
                raise ProcessingError(
                    "Anthropic API does not provide a models list endpoint. "
                    "Use api_models_only=False to list models from local config."
                )
            else:
                # Use local model config - no credentials needed
                for model_id, config in ANTHROPIC_MODELS.items():
                    model = AnthropicModel(model_id, config)
                    models.append(model.dict())
            
            # Return the output
            return AnthropicListModelsOutput(models=models)
            
        except Exception as e:
            raise ProcessingError(f"Failed to list Anthropic models: {str(e)}") 