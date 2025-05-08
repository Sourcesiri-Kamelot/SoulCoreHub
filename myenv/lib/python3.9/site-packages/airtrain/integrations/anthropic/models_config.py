from typing import Dict, NamedTuple, Optional
from decimal import Decimal


class AnthropicModelConfig(NamedTuple):
    display_name: str
    base_model: str
    input_price: Decimal
    cached_write_price: Optional[Decimal]
    cached_read_price: Optional[Decimal]
    output_price: Decimal


ANTHROPIC_MODELS: Dict[str, AnthropicModelConfig] = {
    "claude-3-7-sonnet": AnthropicModelConfig(
        display_name="Claude 3.7 Sonnet",
        base_model="claude-3-7-sonnet",
        input_price=Decimal("3.00"),
        cached_write_price=Decimal("3.75"),
        cached_read_price=Decimal("0.30"),
        output_price=Decimal("15.00"),
    ),
    "claude-3-5-haiku": AnthropicModelConfig(
        display_name="Claude 3.5 Haiku",
        base_model="claude-3-5-haiku",
        input_price=Decimal("0.80"),
        cached_write_price=Decimal("1.00"),
        cached_read_price=Decimal("0.08"),
        output_price=Decimal("4.00"),
    ),
    "claude-3-opus": AnthropicModelConfig(
        display_name="Claude 3 Opus",
        base_model="claude-3-opus",
        input_price=Decimal("15.00"),
        cached_write_price=Decimal("18.75"),
        cached_read_price=Decimal("1.50"),
        output_price=Decimal("75.00"),
    ),
    "claude-3-sonnet": AnthropicModelConfig(
        display_name="Claude 3 Sonnet",
        base_model="claude-3-sonnet",
        input_price=Decimal("3.00"),
        cached_write_price=Decimal("3.75"),
        cached_read_price=Decimal("0.30"),
        output_price=Decimal("15.00"),
    ),
    "claude-3-haiku": AnthropicModelConfig(
        display_name="Claude 3 Haiku",
        base_model="claude-3-haiku",
        input_price=Decimal("0.25"),
        cached_write_price=Decimal("0.31"),
        cached_read_price=Decimal("0.025"),
        output_price=Decimal("1.25"),
    ),
}


def get_model_config(model_id: str) -> AnthropicModelConfig:
    """Get model configuration by model ID"""
    if model_id not in ANTHROPIC_MODELS:
        raise ValueError(f"Model {model_id} not found in Anthropic models")
    return ANTHROPIC_MODELS[model_id]


def get_default_model() -> str:
    """Get the default model ID"""
    return "claude-3-sonnet"


def calculate_cost(
    model_id: str, 
    input_tokens: int, 
    output_tokens: int, 
    use_cached: bool = False,
    cache_type: str = "read"
) -> Decimal:
    """Calculate cost for token usage
    
    Args:
        model_id: The model ID to calculate costs for
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        use_cached: Whether to use cached pricing
        cache_type: Either "read" or "write" for cached pricing type
    """
    config = get_model_config(model_id)
    
    if not use_cached:
        input_cost = config.input_price * Decimal(str(input_tokens))
    else:
        if cache_type == "read" and config.cached_read_price is not None:
            input_cost = config.cached_read_price * Decimal(str(input_tokens))
        elif cache_type == "write" and config.cached_write_price is not None:
            input_cost = config.cached_write_price * Decimal(str(input_tokens))
        else:
            input_cost = config.input_price * Decimal(str(input_tokens))
    
    output_cost = config.output_price * Decimal(str(output_tokens))
    
    return (input_cost + output_cost) / Decimal("1000") 