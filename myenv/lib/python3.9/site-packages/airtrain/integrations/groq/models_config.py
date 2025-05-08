"""Configuration of Groq model capabilities."""

from typing import Dict, Any


# Model configuration with capabilities for each model
GROQ_MODELS_CONFIG = {
    "llama-3.3-70b-versatile": {
        "name": "Llama 3.3 70B Versatile",
        "context_window": 128000,
        "max_completion_tokens": 32768,
        "tool_use": True,
        "parallel_tool_use": True,
        "json_mode": True,
    },
    "llama-3.1-8b-instant": {
        "name": "Llama 3.1 8B Instant",
        "context_window": 128000,
        "max_completion_tokens": 8192,
        "tool_use": True,
        "parallel_tool_use": True,
        "json_mode": True,
    },
    "mixtral-8x7b-32768": {
        "name": "Mixtral 8x7B (32K)",
        "context_window": 32768,
        "max_completion_tokens": 8192,
        "tool_use": True,
        "parallel_tool_use": False,
        "json_mode": True,
    },
    "gemma2-9b-it": {
        "name": "Gemma 2 9B IT",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "tool_use": True,
        "parallel_tool_use": False,
        "json_mode": True,
    },
    "qwen-qwq-32b": {
        "name": "Qwen QWQ 32B",
        "context_window": 128000,
        "max_completion_tokens": 16384,
        "tool_use": True,
        "parallel_tool_use": True,
        "json_mode": True,
    },
    "qwen-2.5-coder-32b": {
        "name": "Qwen 2.5 Coder 32B",
        "context_window": 128000,
        "max_completion_tokens": 16384,
        "tool_use": True,
        "parallel_tool_use": True,
        "json_mode": True,
    },
    "qwen-2.5-32b": {
        "name": "Qwen 2.5 32B",
        "context_window": 128000,
        "max_completion_tokens": 16384,
        "tool_use": True,
        "parallel_tool_use": True,
        "json_mode": True,
    },
    "deepseek-r1-distill-qwen-32b": {
        "name": "DeepSeek R1 Distill Qwen 32B",
        "context_window": 128000,
        "max_completion_tokens": 16384,
        "tool_use": True,
        "parallel_tool_use": True,
        "json_mode": True,
    },
    "deepseek-r1-distill-llama-70b": {
        "name": "DeepSeek R1 Distill Llama 70B",
        "context_window": 128000,
        "max_completion_tokens": 16384,
        "tool_use": True,
        "parallel_tool_use": True,
        "json_mode": True,
    },
    "deepseek-r1-distill-llama-70b-specdec": {
        "name": "DeepSeek R1 Distill Llama 70B SpecDec",
        "context_window": 128000,
        "max_completion_tokens": 16384,
        "tool_use": False,
        "parallel_tool_use": False,
        "json_mode": False,
    },
    "llama3-70b-8192": {
        "name": "Llama 3 70B (8K)",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "tool_use": False,
        "parallel_tool_use": False,
        "json_mode": False,
    },
    "llama3-8b-8192": {
        "name": "Llama 3 8B (8K)",
        "context_window": 8192,
        "max_completion_tokens": 4096,
        "tool_use": False,
        "parallel_tool_use": False,
        "json_mode": False,
    },
}


def get_model_config(model_id: str) -> Dict[str, Any]:
    """
    Get the configuration for a specific model.
    
    Args:
        model_id: The model ID to get configuration for
        
    Returns:
        Dict with model configuration
        
    Raises:
        ValueError: If model_id is not found in configuration
    """
    if model_id in GROQ_MODELS_CONFIG:
        return GROQ_MODELS_CONFIG[model_id]
    
    # Try to find a match with different format or case
    normalized_id = model_id.lower().replace("-", "").replace("_", "")
    for config_id, config in GROQ_MODELS_CONFIG.items():
        if normalized_id == config_id.lower().replace("-", "").replace("_", ""):
            return config
    
    # Default configuration for unknown models
    return {
        "name": model_id,
        "context_window": 4096,  # Conservative default
        "max_completion_tokens": 1024,  # Conservative default
        "tool_use": False,
        "parallel_tool_use": False,
        "json_mode": False,
    }


def get_default_model() -> str:
    """Get the default model ID for Groq."""
    return "llama-3.3-70b-versatile"


def supports_tool_use(model_id: str) -> bool:
    """Check if a model supports tool use."""
    return get_model_config(model_id).get("tool_use", False)


def supports_parallel_tool_use(model_id: str) -> bool:
    """Check if a model supports parallel tool use."""
    return get_model_config(model_id).get("parallel_tool_use", False)


def supports_json_mode(model_id: str) -> bool:
    """Check if a model supports JSON mode."""
    return get_model_config(model_id).get("json_mode", False)


def get_max_completion_tokens(model_id: str) -> int:
    """Get the maximum number of completion tokens for a model."""
    return get_model_config(model_id).get("max_completion_tokens", 1024) 