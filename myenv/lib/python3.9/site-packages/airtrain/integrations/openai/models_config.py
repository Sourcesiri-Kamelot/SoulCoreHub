from typing import Dict, NamedTuple, Optional
from decimal import Decimal


class OpenAIModelConfig(NamedTuple):
    display_name: str
    base_model: str
    input_price: Decimal
    cached_input_price: Optional[Decimal]
    output_price: Decimal


OPENAI_MODELS: Dict[str, OpenAIModelConfig] = {
    "gpt-4.5-preview": OpenAIModelConfig(
        display_name="GPT-4.5 Preview",
        base_model="gpt-4.5-preview",
        input_price=Decimal("75.00"),
        cached_input_price=Decimal("37.50"),
        output_price=Decimal("150.00"),
    ),
    "gpt-4.5-preview-2025-02-27": OpenAIModelConfig(
        display_name="GPT-4.5 Preview (2025-02-27)",
        base_model="gpt-4.5-preview",
        input_price=Decimal("75.00"),
        cached_input_price=Decimal("37.50"),
        output_price=Decimal("150.00"),
    ),
    "gpt-4o": OpenAIModelConfig(
        display_name="GPT-4 Optimized",
        base_model="gpt-4o",
        input_price=Decimal("2.50"),
        cached_input_price=Decimal("1.25"),
        output_price=Decimal("10.00"),
    ),
    "gpt-4o-2024-08-06": OpenAIModelConfig(
        display_name="GPT-4 Optimized (2024-08-06)",
        base_model="gpt-4o",
        input_price=Decimal("2.50"),
        cached_input_price=Decimal("1.25"),
        output_price=Decimal("10.00"),
    ),
    "gpt-4o-audio-preview": OpenAIModelConfig(
        display_name="GPT-4 Optimized Audio Preview",
        base_model="gpt-4o-audio-preview",
        input_price=Decimal("2.50"),
        cached_input_price=None,
        output_price=Decimal("10.00"),
    ),
    "gpt-4o-audio-preview-2024-12-17": OpenAIModelConfig(
        display_name="GPT-4 Optimized Audio Preview (2024-12-17)",
        base_model="gpt-4o-audio-preview",
        input_price=Decimal("2.50"),
        cached_input_price=None,
        output_price=Decimal("10.00"),
    ),
    "gpt-4o-realtime-preview": OpenAIModelConfig(
        display_name="GPT-4 Optimized Realtime Preview",
        base_model="gpt-4o-realtime-preview",
        input_price=Decimal("5.00"),
        cached_input_price=Decimal("2.50"),
        output_price=Decimal("20.00"),
    ),
    "gpt-4o-realtime-preview-2024-12-17": OpenAIModelConfig(
        display_name="GPT-4 Optimized Realtime Preview (2024-12-17)",
        base_model="gpt-4o-realtime-preview",
        input_price=Decimal("5.00"),
        cached_input_price=Decimal("2.50"),
        output_price=Decimal("20.00"),
    ),
    "gpt-4o-mini": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini",
        base_model="gpt-4o-mini",
        input_price=Decimal("0.15"),
        cached_input_price=Decimal("0.075"),
        output_price=Decimal("0.60"),
    ),
    "gpt-4o-mini-2024-07-18": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini (2024-07-18)",
        base_model="gpt-4o-mini",
        input_price=Decimal("0.15"),
        cached_input_price=Decimal("0.075"),
        output_price=Decimal("0.60"),
    ),
    "gpt-4o-mini-audio-preview": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini Audio Preview",
        base_model="gpt-4o-mini-audio-preview",
        input_price=Decimal("0.15"),
        cached_input_price=None,
        output_price=Decimal("0.60"),
    ),
    "gpt-4o-mini-audio-preview-2024-12-17": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini Audio Preview (2024-12-17)",
        base_model="gpt-4o-mini-audio-preview",
        input_price=Decimal("0.15"),
        cached_input_price=None,
        output_price=Decimal("0.60"),
    ),
    "gpt-4o-mini-realtime-preview": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini Realtime Preview",
        base_model="gpt-4o-mini-realtime-preview",
        input_price=Decimal("0.60"),
        cached_input_price=Decimal("0.30"),
        output_price=Decimal("2.40"),
    ),
    "gpt-4o-mini-realtime-preview-2024-12-17": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini Realtime Preview (2024-12-17)",
        base_model="gpt-4o-mini-realtime-preview",
        input_price=Decimal("0.60"),
        cached_input_price=Decimal("0.30"),
        output_price=Decimal("2.40"),
    ),
    "o1": OpenAIModelConfig(
        display_name="O1",
        base_model="o1",
        input_price=Decimal("15.00"),
        cached_input_price=Decimal("7.50"),
        output_price=Decimal("60.00"),
    ),
    "o1-2024-12-17": OpenAIModelConfig(
        display_name="O1 (2024-12-17)",
        base_model="o1",
        input_price=Decimal("15.00"),
        cached_input_price=Decimal("7.50"),
        output_price=Decimal("60.00"),
    ),
    "o3-mini": OpenAIModelConfig(
        display_name="O3 Mini",
        base_model="o3-mini",
        input_price=Decimal("1.10"),
        cached_input_price=Decimal("0.55"),
        output_price=Decimal("4.40"),
    ),
    "o3-mini-2025-01-31": OpenAIModelConfig(
        display_name="O3 Mini (2025-01-31)",
        base_model="o3-mini",
        input_price=Decimal("1.10"),
        cached_input_price=Decimal("0.55"),
        output_price=Decimal("4.40"),
    ),
    "o1-mini": OpenAIModelConfig(
        display_name="O1 Mini",
        base_model="o1-mini",
        input_price=Decimal("1.10"),
        cached_input_price=Decimal("0.55"),
        output_price=Decimal("4.40"),
    ),
    "o1-mini-2024-09-12": OpenAIModelConfig(
        display_name="O1 Mini (2024-09-12)",
        base_model="o1-mini",
        input_price=Decimal("1.10"),
        cached_input_price=Decimal("0.55"),
        output_price=Decimal("4.40"),
    ),
    "gpt-4o-mini-search-preview": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini Search Preview",
        base_model="gpt-4o-mini-search-preview",
        input_price=Decimal("0.15"),
        cached_input_price=None,
        output_price=Decimal("0.60"),
    ),
    "gpt-4o-mini-search-preview-2025-03-11": OpenAIModelConfig(
        display_name="GPT-4 Optimized Mini Search Preview (2025-03-11)",
        base_model="gpt-4o-mini-search-preview",
        input_price=Decimal("0.15"),
        cached_input_price=None,
        output_price=Decimal("0.60"),
    ),
    "gpt-4o-search-preview": OpenAIModelConfig(
        display_name="GPT-4 Optimized Search Preview",
        base_model="gpt-4o-search-preview",
        input_price=Decimal("2.50"),
        cached_input_price=None,
        output_price=Decimal("10.00"),
    ),
    "gpt-4o-search-preview-2025-03-11": OpenAIModelConfig(
        display_name="GPT-4 Optimized Search Preview (2025-03-11)",
        base_model="gpt-4o-search-preview",
        input_price=Decimal("2.50"),
        cached_input_price=None,
        output_price=Decimal("10.00"),
    ),
    "computer-use-preview": OpenAIModelConfig(
        display_name="Computer Use Preview",
        base_model="computer-use-preview",
        input_price=Decimal("3.00"),
        cached_input_price=None,
        output_price=Decimal("12.00"),
    ),
    "computer-use-preview-2025-03-11": OpenAIModelConfig(
        display_name="Computer Use Preview (2025-03-11)",
        base_model="computer-use-preview",
        input_price=Decimal("3.00"),
        cached_input_price=None,
        output_price=Decimal("12.00"),
    ),
}


def get_model_config(model_id: str) -> OpenAIModelConfig:
    """Get model configuration by model ID"""
    if model_id not in OPENAI_MODELS:
        raise ValueError(f"Model {model_id} not found in OpenAI models")
    return OPENAI_MODELS[model_id]


def get_default_model() -> str:
    """Get the default model ID"""
    return "gpt-4o"


def calculate_cost(
    model_id: str, input_tokens: int, output_tokens: int, use_cached: bool = False
) -> Decimal:
    """Calculate cost for token usage"""
    config = get_model_config(model_id)
    input_price = (
        config.cached_input_price
        if (use_cached and config.cached_input_price is not None)
        else config.input_price
    )
    return (
        input_price * Decimal(str(input_tokens))
        + config.output_price * Decimal(str(output_tokens))
    ) / Decimal("1000")
