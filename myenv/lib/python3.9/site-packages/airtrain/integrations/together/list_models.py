from typing import Optional
import requests
from pydantic import Field

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import TogetherAICredentials
from .models import TogetherModel


class TogetherListModelsInput(InputSchema):
    """Schema for Together AI list models input"""
    pass


class TogetherListModelsOutput(OutputSchema):
    """Schema for Together AI list models output"""
    
    data: list[TogetherModel] = Field(
        default_factory=list,
        description="List of Together AI models"
    )
    object: Optional[str] = Field(
        default=None, 
        description="Object type"
    )


class TogetherListModelsSkill(Skill[TogetherListModelsInput, TogetherListModelsOutput]):
    """Skill for listing Together AI models"""

    input_schema = TogetherListModelsInput
    output_schema = TogetherListModelsOutput
    
    def __init__(self, credentials: Optional[TogetherAICredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or TogetherAICredentials.from_env()
        self.base_url = "https://api.together.xyz/v1"
    
    def process(
        self, input_data: TogetherListModelsInput
    ) -> TogetherListModelsOutput:
        """Process the input and return a list of models."""
        try:
            # Build the URL
            url = f"{self.base_url}/models"
            
            # Make the request
            headers = {
                "Authorization": (
                    f"Bearer {self.credentials.together_api_key.get_secret_value()}"
                ),
                "accept": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Convert the models to TogetherModel objects
            models = []
            for model_data in result:
                models.append(TogetherModel(**model_data))
            
            # Return the output
            return TogetherListModelsOutput(
                data=models,
            )
            
        except requests.RequestException as e:
            raise ProcessingError(f"Failed to list Together AI models: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Error listing Together AI models: {str(e)}") 