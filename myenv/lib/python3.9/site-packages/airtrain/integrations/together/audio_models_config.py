from typing import Dict, NamedTuple


class AudioModelConfig(NamedTuple):
    organization: str
    display_name: str


TOGETHER_AUDIO_MODELS: Dict[str, AudioModelConfig] = {
    "Cartesia/Sonic": AudioModelConfig(
        organization="Cartesia", display_name="Cartesia/Sonic"
    )
}


def get_audio_model_config(model_id: str) -> AudioModelConfig:
    """Get audio model configuration by model ID"""
    if model_id not in TOGETHER_AUDIO_MODELS:
        raise ValueError(f"Model {model_id} not found in Together AI audio models")
    return TOGETHER_AUDIO_MODELS[model_id]


def list_audio_models_by_organization(organization: str) -> Dict[str, AudioModelConfig]:
    """Get all audio models for a specific organization"""
    return {
        model_id: config
        for model_id, config in TOGETHER_AUDIO_MODELS.items()
        if config.organization.lower() == organization.lower()
    }


def get_default_audio_model() -> str:
    """Get the default audio model ID"""
    return "Cartesia/Sonic"
