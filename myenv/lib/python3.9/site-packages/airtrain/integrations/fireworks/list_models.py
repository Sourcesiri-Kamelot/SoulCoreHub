from typing import Optional, List
import requests
from pydantic import Field

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import FireworksCredentials
from .models import FireworksModel


class FireworksListModelsInput(InputSchema):
    """Schema for Fireworks AI list models input"""

    account_id: str = Field(..., description="The Account Id")
    page_size: Optional[int] = Field(
        default=50, 
        description=(
            "The maximum number of models to return. The maximum page_size is 200, "
            "values above 200 will be coerced to 200."
        ),
        le=200
    )
    page_token: Optional[str] = Field(
        default=None,
        description=(
            "A page token, received from a previous ListModels call. Provide this "
            "to retrieve the subsequent page. When paginating, all other parameters "
            "provided to ListModels must match the call that provided the page token."
        )
    )
    filter: Optional[str] = Field(
        default=None,
        description=(
            "Only model satisfying the provided filter (if specified) will be "
            "returned. See https://google.aip.dev/160 for the filter grammar."
        )
    )
    order_by: Optional[str] = Field(
        default=None,
        description=(
            "A comma-separated list of fields to order by. e.g. \"foo,bar\" "
            "The default sort order is ascending. To specify a descending order for a "
            "field, append a \" desc\" suffix. e.g. \"foo desc,bar\" "
            "Subfields are specified with a \".\" character. e.g. \"foo.bar\" "
            "If not specified, the default order is by \"name\"."
        )
    )


class FireworksListModelsOutput(OutputSchema):
    """Schema for Fireworks AI list models output"""

    models: List[FireworksModel] = Field(
        default_factory=list, 
        description="List of Fireworks models"
    )
    next_page_token: Optional[str] = Field(
        default=None, 
        description="Token for retrieving the next page of results"
    )
    total_size: Optional[int] = Field(
        default=None, 
        description="Total number of models available"
    )


class FireworksListModelsSkill(
    Skill[FireworksListModelsInput, FireworksListModelsOutput]
):
    """Skill for listing Fireworks AI models"""

    input_schema = FireworksListModelsInput
    output_schema = FireworksListModelsOutput
    
    def __init__(self, credentials: Optional[FireworksCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or FireworksCredentials.from_env()
        self.base_url = "https://api.fireworks.ai/v1"
    
    def process(
        self, input_data: FireworksListModelsInput
    ) -> FireworksListModelsOutput:
        """Process the input and return a list of models."""
        try:
            # Build the URL
            url = f"{self.base_url}/accounts/{input_data.account_id}/models"
            
            # Prepare query parameters
            params = {}
            if input_data.page_size:
                params["pageSize"] = input_data.page_size
            if input_data.page_token:
                params["pageToken"] = input_data.page_token
            if input_data.filter:
                params["filter"] = input_data.filter
            if input_data.order_by:
                params["orderBy"] = input_data.order_by
            
            # Make the request
            headers = {
                "Authorization": (
                    f"Bearer {self.credentials.fireworks_api_key.get_secret_value()}"
                )
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Convert the models to FireworksModel objects
            models = []
            for model_data in result.get("models", []):
                models.append(FireworksModel(**model_data))
            
            # Return the output
            return FireworksListModelsOutput(
                models=models,
                next_page_token=result.get("nextPageToken"),
                total_size=result.get("totalSize")
            )
            
        except requests.RequestException as e:
            raise ProcessingError(f"Failed to list Fireworks models: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Error listing Fireworks models: {str(e)}") 