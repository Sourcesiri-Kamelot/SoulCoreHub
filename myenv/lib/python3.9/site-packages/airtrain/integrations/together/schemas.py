from typing import List, Optional
from pydantic import Field, BaseModel
from airtrain.core.schemas import InputSchema, OutputSchema


class RerankResult(BaseModel):
    """Schema for individual rerank result"""

    index: int = Field(..., description="Index of the document in original list")
    relevance_score: float = Field(..., description="Relevance score for the document")
    document: str = Field(..., description="The document content")


class TogetherAIRerankInput(InputSchema):
    """Schema for Together AI rerank input"""

    query: str = Field(..., description="Query to rank documents against")
    documents: List[str] = Field(..., description="List of documents to rank")
    model: str = Field(
        default="Salesforce/Llama-Rank-v1",
        description="Together AI rerank model to use",
    )
    top_n: Optional[int] = Field(
        default=None,
        description="Number of top results to return. If None, returns all results",
    )


class TogetherAIRerankOutput(OutputSchema):
    """Schema for Together AI rerank output"""

    results: List[RerankResult] = Field(..., description="Ranked results")
    used_model: str = Field(..., description="Model used for ranking")
