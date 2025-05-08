from typing import Dict, NamedTuple


class RerankModelConfig(NamedTuple):
    organization: str
    display_name: str
    model_size: str
    max_doc_size: int
    max_docs: int


TOGETHER_RERANK_MODELS: Dict[str, RerankModelConfig] = {
    "Salesforce/Llama-Rank-v1": RerankModelConfig(
        organization="Salesforce",
        display_name="LlamaRank",
        model_size="8B",
        max_doc_size=8192,
        max_docs=1024,
    )
}


def get_rerank_model_config(model_id: str) -> RerankModelConfig:
    """Get rerank model configuration by model ID"""
    if model_id not in TOGETHER_RERANK_MODELS:
        raise ValueError(f"Model {model_id} not found in Together AI rerank models")
    return TOGETHER_RERANK_MODELS[model_id]


def list_rerank_models_by_organization(
    organization: str,
) -> Dict[str, RerankModelConfig]:
    """Get all rerank models for a specific organization"""
    return {
        model_id: config
        for model_id, config in TOGETHER_RERANK_MODELS.items()
        if config.organization.lower() == organization.lower()
    }


def get_default_rerank_model() -> str:
    """Get the default rerank model ID"""
    return "Salesforce/Llama-Rank-v1"
