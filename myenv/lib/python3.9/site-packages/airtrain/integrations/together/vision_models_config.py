from typing import Dict, NamedTuple


class VisionModelConfig(NamedTuple):
    organization: str
    display_name: str
    context_length: int


TOGETHER_VISION_MODELS: Dict[str, VisionModelConfig] = {
    "meta-llama/Llama-Vision-Free": VisionModelConfig(
        organization="Meta",
        display_name="(Free) Llama 3.2 11B Vision Instruct Turbo",
        context_length=131072,
    ),
    "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo": VisionModelConfig(
        organization="Meta",
        display_name="Llama 3.2 11B Vision Instruct Turbo",
        context_length=131072,
    ),
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo": VisionModelConfig(
        organization="Meta",
        display_name="Llama 3.2 90B Vision Instruct Turbo",
        context_length=131072,
    ),
}


def get_vision_model_config(model_id: str) -> VisionModelConfig:
    """Get vision model configuration by model ID"""
    if model_id not in TOGETHER_VISION_MODELS:
        raise ValueError(f"Model {model_id} not found in Together AI vision models")
    return TOGETHER_VISION_MODELS[model_id]


def list_vision_models_by_organization(
    organization: str,
) -> Dict[str, VisionModelConfig]:
    """Get all vision models for a specific organization"""
    return {
        model_id: config
        for model_id, config in TOGETHER_VISION_MODELS.items()
        if config.organization.lower() == organization.lower()
    }


def get_default_vision_model() -> str:
    """Get the default vision model ID"""
    return "meta-llama/Llama-Vision-Free"
