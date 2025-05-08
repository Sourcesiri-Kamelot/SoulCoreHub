from typing import Dict, NamedTuple


class EmbeddingModelConfig(NamedTuple):
    organization: str
    display_name: str
    model_size: str
    embedding_dimension: int
    context_window: int


TOGETHER_EMBEDDING_MODELS: Dict[str, EmbeddingModelConfig] = {
    "togethercomputer/m2-bert-80M-2k-retrieval": EmbeddingModelConfig(
        organization="Together",
        display_name="M2-BERT-80M-2K-Retrieval",
        model_size="80M",
        embedding_dimension=768,
        context_window=2048,
    ),
    "togethercomputer/m2-bert-80M-8k-retrieval": EmbeddingModelConfig(
        organization="Together",
        display_name="M2-BERT-80M-8K-Retrieval",
        model_size="80M",
        embedding_dimension=768,
        context_window=8192,
    ),
    "togethercomputer/m2-bert-80M-32k-retrieval": EmbeddingModelConfig(
        organization="Together",
        display_name="M2-BERT-80M-32K-Retrieval",
        model_size="80M",
        embedding_dimension=768,
        context_window=32768,
    ),
    "WhereIsAI/UAE-Large-V1": EmbeddingModelConfig(
        organization="WhereIsAI",
        display_name="UAE-Large-v1",
        model_size="326M",
        embedding_dimension=1024,
        context_window=512,
    ),
    "BAAI/bge-large-en-v1.5": EmbeddingModelConfig(
        organization="BAAI",
        display_name="BGE-Large-EN-v1.5",
        model_size="326M",
        embedding_dimension=1024,
        context_window=512,
    ),
    "BAAI/bge-base-en-v1.5": EmbeddingModelConfig(
        organization="BAAI",
        display_name="BGE-Base-EN-v1.5",
        model_size="102M",
        embedding_dimension=768,
        context_window=512,
    ),
    "sentence-transformers/msmarco-bert-base-dot-v5": EmbeddingModelConfig(
        organization="sentence-transformers",
        display_name="Sentence-BERT",
        model_size="110M",
        embedding_dimension=768,
        context_window=512,
    ),
    "bert-base-uncased": EmbeddingModelConfig(
        organization="Hugging Face",
        display_name="BERT",
        model_size="110M",
        embedding_dimension=768,
        context_window=512,
    ),
}


def get_embedding_model_config(model_id: str) -> EmbeddingModelConfig:
    """Get embedding model configuration by model ID"""
    if model_id not in TOGETHER_EMBEDDING_MODELS:
        raise ValueError(f"Model {model_id} not found in Together AI embedding models")
    return TOGETHER_EMBEDDING_MODELS[model_id]


def list_embedding_models_by_organization(
    organization: str,
) -> Dict[str, EmbeddingModelConfig]:
    """Get all embedding models for a specific organization"""
    return {
        model_id: config
        for model_id, config in TOGETHER_EMBEDDING_MODELS.items()
        if config.organization.lower() == organization.lower()
    }


def get_default_embedding_model() -> str:
    """Get the default embedding model ID"""
    return "togethercomputer/m2-bert-80M-32k-retrieval"
