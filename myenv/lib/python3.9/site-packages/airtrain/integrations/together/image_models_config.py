from typing import Dict, NamedTuple, Optional


class ImageModelConfig(NamedTuple):
    organization: str
    display_name: str
    default_steps: Optional[int]


TOGETHER_IMAGE_MODELS: Dict[str, ImageModelConfig] = {
    "black-forest-labs/FLUX.1-schnell-Free": ImageModelConfig(
        organization="Black Forest Labs",
        display_name="Flux.1 [schnell] (free)",
        default_steps=None,
    ),
    "black-forest-labs/FLUX.1-schnell": ImageModelConfig(
        organization="Black Forest Labs",
        display_name="Flux.1 [schnell] (Turbo)",
        default_steps=4,
    ),
    "black-forest-labs/FLUX.1-dev": ImageModelConfig(
        organization="Black Forest Labs", display_name="Flux.1 Dev", default_steps=28
    ),
    "black-forest-labs/FLUX.1-canny": ImageModelConfig(
        organization="Black Forest Labs", display_name="Flux.1 Canny", default_steps=28
    ),
    "black-forest-labs/FLUX.1-depth": ImageModelConfig(
        organization="Black Forest Labs", display_name="Flux.1 Depth", default_steps=28
    ),
    "black-forest-labs/FLUX.1-redux": ImageModelConfig(
        organization="Black Forest Labs", display_name="Flux.1 Redux", default_steps=28
    ),
    "black-forest-labs/FLUX.1.1-pro": ImageModelConfig(
        organization="Black Forest Labs",
        display_name="Flux1.1 [pro]",
        default_steps=None,
    ),
    "black-forest-labs/FLUX.1-pro": ImageModelConfig(
        organization="Black Forest Labs",
        display_name="Flux.1 [pro]",
        default_steps=None,
    ),
    "stabilityai/stable-diffusion-xl-base-1.0": ImageModelConfig(
        organization="Stability AI",
        display_name="Stable Diffusion XL 1.0",
        default_steps=None,
    ),
}


def get_image_model_config(model_id: str) -> ImageModelConfig:
    """Get image model configuration by model ID"""
    if model_id not in TOGETHER_IMAGE_MODELS:
        raise ValueError(f"Model {model_id} not found in Together AI image models")
    return TOGETHER_IMAGE_MODELS[model_id]


def list_image_models_by_organization(organization: str) -> Dict[str, ImageModelConfig]:
    """Get all image models for a specific organization"""
    return {
        model_id: config
        for model_id, config in TOGETHER_IMAGE_MODELS.items()
        if config.organization.lower() == organization.lower()
    }


def get_default_image_model() -> str:
    """Get the default image model ID"""
    return "black-forest-labs/FLUX.1-schnell-Free"
