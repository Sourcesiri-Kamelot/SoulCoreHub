from typing import Optional
from together import Together
from airtrain.core.skills import Skill, ProcessingError
from .credentials import TogetherAICredentials
from .schemas import TogetherAIRerankInput, TogetherAIRerankOutput, RerankResult
from .rerank_models_config import get_rerank_model_config


class TogetherAIRerankSkill(Skill[TogetherAIRerankInput, TogetherAIRerankOutput]):
    """Skill for reranking documents using Together AI"""

    input_schema = TogetherAIRerankInput
    output_schema = TogetherAIRerankOutput

    def __init__(self, credentials: Optional[TogetherAICredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or TogetherAICredentials.from_env()
        self.client = Together(
            api_key=self.credentials.together_api_key.get_secret_value()
        )

    def process(self, input_data: TogetherAIRerankInput) -> TogetherAIRerankOutput:
        try:
            # Validate the model exists in our config
            get_rerank_model_config(input_data.model)

            # Call Together AI rerank API
            response = self.client.rerank.create(
                model=input_data.model,
                query=input_data.query,
                documents=input_data.documents,
                top_n=input_data.top_n,
            )

            # Transform results
            results = [
                RerankResult(
                    index=result.index,
                    relevance_score=result.relevance_score,
                    document=input_data.documents[result.index],
                )
                for result in response.results
            ]

            return TogetherAIRerankOutput(results=results, used_model=input_data.model)

        except Exception as e:
            raise ProcessingError(f"Together AI reranking failed: {str(e)}")
