"""Configuration of Perplexity AI model capabilities."""

from typing import Dict, Any


# Model configuration with capabilities for each Perplexity AI model
PERPLEXITY_MODELS_CONFIG = {
    # Search Models
    "sonar-pro": {
        "name": "Sonar Pro",
        "description": "Advanced search offering with grounding, supporting complex queries and follow-ups.",
        "category": "search",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "citations": True,
        "search": True,
    },
    "sonar": {
        "name": "Sonar",
        "description": "Lightweight, cost-effective search model with grounding.",
        "category": "search",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "citations": True,
        "search": True,
    },
    # Research Models
    "sonar-deep-research": {
        "name": "Sonar Deep Research",
        "description": "Expert-level research model conducting exhaustive searches and generating comprehensive reports.",
        "category": "research",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "citations": True,
        "search": True,
    },
    # Reasoning Models
    "sonar-reasoning-pro": {
        "name": "Sonar Reasoning Pro",
        "description": "Premier reasoning offering powered by DeepSeek R1 with Chain of Thought (CoT).",
        "category": "reasoning",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "citations": True,
        "search": True,
        "chain_of_thought": True,
    },
    "sonar-reasoning": {
        "name": "Sonar Reasoning",
        "description": "Fast, real-time reasoning model designed for quick problem-solving with search.",
        "category": "reasoning",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "citations": True,
        "search": True,
        "chain_of_thought": True,
    },
    # Offline Models
    "r1-1776": {
        "name": "R1-1776",
        "description": "A version of DeepSeek R1 post-trained for uncensored, unbiased, and factual information.",
        "category": "offline",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "citations": False,
        "search": False,
    },
}


def get_model_config(model_id: str) -> Dict[str, Any]:
    """
    Get the configuration for a specific Perplexity AI model.

    Args:
        model_id: The model ID to get configuration for

    Returns:
        Dict with model configuration

    Raises:
        ValueError: If model_id is not found in configuration
    """
    if model_id in PERPLEXITY_MODELS_CONFIG:
        return PERPLEXITY_MODELS_CONFIG[model_id]

    # Try to find a match with different format or case
    normalized_id = model_id.lower().replace("-", "").replace("_", "")
    for config_id, config in PERPLEXITY_MODELS_CONFIG.items():
        if normalized_id == config_id.lower().replace("-", "").replace("_", ""):
            return config

    # If model not found, raise an error
    raise ValueError(
        f"Model '{model_id}' not found in Perplexity AI models configuration"
    )


def get_default_model() -> str:
    """Get the default model ID for Perplexity AI."""
    return "sonar-pro"


def supports_citations(model_id: str) -> bool:
    """Check if a model supports citations."""
    return get_model_config(model_id).get("citations", False)


def supports_search(model_id: str) -> bool:
    """Check if a model uses search capabilities."""
    return get_model_config(model_id).get("search", False)


def get_models_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """
    Get all models belonging to a specific category.

    Args:
        category: Category to filter by ('search', 'research', 'reasoning', 'offline')

    Returns:
        Dict of model IDs and their configurations that match the category
    """
    return {
        model_id: config
        for model_id, config in PERPLEXITY_MODELS_CONFIG.items()
        if config.get("category") == category
    }
