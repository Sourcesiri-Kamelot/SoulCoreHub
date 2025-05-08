from typing import List, Optional, Dict, Any
from pydantic import Field, BaseModel


class FireworksMessage(BaseModel):
    """Schema for Fireworks chat message"""

    content: str
    role: str = Field(..., pattern="^(system|user|assistant)$")


class FireworksUsage(BaseModel):
    """Schema for Fireworks API usage statistics"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class FireworksResponse(BaseModel):
    """Schema for Fireworks API response"""

    id: str
    choices: List[Dict[str, Any]]
    created: int
    model: str
    usage: FireworksUsage


class FireworksModelStatus(BaseModel):
    """Schema for Fireworks model status"""
    # This would be filled with actual fields from the API response


class FireworksModelBaseDetails(BaseModel):
    """Schema for Fireworks base model details"""
    # This would be filled with actual fields from the API response


class FireworksPeftDetails(BaseModel):
    """Schema for Fireworks PEFT details"""
    # This would be filled with actual fields from the API response


class FireworksConversationConfig(BaseModel):
    """Schema for Fireworks conversation configuration"""
    # This would be filled with actual fields from the API response


class FireworksModelDeployedRef(BaseModel):
    """Schema for Fireworks deployed model reference"""
    # This would be filled with actual fields from the API response


class FireworksDeprecationDate(BaseModel):
    """Schema for Fireworks deprecation date"""
    # This would be filled with actual fields from the API response


class FireworksModel(BaseModel):
    """Schema for a Fireworks model"""
    
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    create_time: Optional[str] = None
    created_by: Optional[str] = None
    state: Optional[str] = None
    status: Optional[Dict[str, Any]] = None
    kind: Optional[str] = None
    github_url: Optional[str] = None
    hugging_face_url: Optional[str] = None
    base_model_details: Optional[Dict[str, Any]] = None
    peft_details: Optional[Dict[str, Any]] = None
    teft_details: Optional[Dict[str, Any]] = None
    public: Optional[bool] = None
    conversation_config: Optional[Dict[str, Any]] = None
    context_length: Optional[int] = None
    supports_image_input: Optional[bool] = None
    supports_tools: Optional[bool] = None
    imported_from: Optional[str] = None
    fine_tuning_job: Optional[str] = None
    default_draft_model: Optional[str] = None
    default_draft_token_count: Optional[int] = None
    precisions: Optional[List[str]] = None
    deployed_model_refs: Optional[List[Dict[str, Any]]] = None
    cluster: Optional[str] = None
    deprecation_date: Optional[Dict[str, Any]] = None
    calibrated: Optional[bool] = None
    tunable: Optional[bool] = None
    supports_lora: Optional[bool] = None
    use_hf_apply_chat_template: Optional[bool] = None


class ListModelsInput(BaseModel):
    """Schema for listing Fireworks models input"""
    
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


class ListModelsOutput(BaseModel):
    """Schema for listing Fireworks models output"""
    
    models: List[FireworksModel]
    next_page_token: Optional[str] = None
    total_size: Optional[int] = None
