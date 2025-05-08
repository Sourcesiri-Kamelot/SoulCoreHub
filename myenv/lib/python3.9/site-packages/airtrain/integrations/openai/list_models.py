from typing import Optional, List, Dict, Any
from pydantic import Field

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import OpenAICredentials
from .models_config import OPENAI_MODELS, OpenAIModelConfig


class OpenAIModel:
    """Class to represent an OpenAI model."""
    
    def __init__(self, model_id: str, config: OpenAIModelConfig):
        """Initialize the OpenAI model."""
        self.id = model_id
        self.display_name = config.display_name
        self.base_model = config.base_model
        self.input_price = config.input_price
        self.cached_input_price = config.cached_input_price
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
        if self.cached_input_price is not None:
            result["cached_input_price"] = float(self.cached_input_price)
        elif not exclude_none:
            result["cached_input_price"] = None
        return result


class OpenAIListModelsInput(InputSchema):
    """Schema for OpenAI list models input"""
    
    api_models_only: bool = Field(
        default=False,
        description=(
            "If True, fetch models from the API only. If False, use local config."
        )
    )


class OpenAIListModelsOutput(OutputSchema):
    """Schema for OpenAI list models output"""
    
    models: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of OpenAI models"
    )


class OpenAIListModelsSkill(Skill[OpenAIListModelsInput, OpenAIListModelsOutput]):
    """Skill for listing OpenAI models"""

    input_schema = OpenAIListModelsInput
    output_schema = OpenAIListModelsOutput
    
    def __init__(self, credentials: Optional[OpenAICredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials
    
    def process(
        self, input_data: OpenAIListModelsInput
    ) -> OpenAIListModelsOutput:
        """Process the input and return a list of models."""
        try:
            models = []
            
            if input_data.api_models_only:
                # Fetch models from OpenAI API - requires credentials
                if not self.credentials:
                    raise ProcessingError(
                        "OpenAI credentials required for API models"
                    )
                
                from openai import OpenAI
                client = OpenAI(
                    api_key=self.credentials.openai_api_key.get_secret_value(),
                    organization=self.credentials.openai_organization_id,
                )
                
                # Make API call to get models
                response = client.models.list()
                
                # Convert response to our format
                for model in response.data:
                    models.append({
                        "id": model.id,
                        "display_name": model.id,  # API doesn't provide display_name
                        "base_model": model.id,    # API doesn't provide base_model
                        "created": model.created,
                        "owned_by": model.owned_by,
                        # Pricing info not available from API
                    })
            else:
                # Use local model config - no credentials needed
                for model_id, config in OPENAI_MODELS.items():
                    model = OpenAIModel(model_id, config)
                    models.append(model.dict())
            
            # Return the output
            return OpenAIListModelsOutput(models=models)
            
        except Exception as e:
            raise ProcessingError(f"Failed to list OpenAI models: {str(e)}") 