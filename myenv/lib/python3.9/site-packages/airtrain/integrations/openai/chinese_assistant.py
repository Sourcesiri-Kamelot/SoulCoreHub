from typing import Optional, TypeVar
from pydantic import Field
from .skills import OpenAIChatSkill, OpenAIInput, OpenAIOutput
from .credentials import OpenAICredentials

T = TypeVar("T", bound=OpenAIInput)


class ChineseAssistantInput(OpenAIInput):
    """Schema for Chinese Assistant input"""

    user_input: str = Field(
        ..., description="User's input text (can be in any language)"
    )
    system_prompt: str = Field(
        default="你是一个有帮助的助手。请用中文回答所有问题，即使问题是用其他语言问的。回答要准确、礼貌、专业。",
        description="System prompt in Chinese",
    )
    model: str = Field(default="gpt-4o", description="OpenAI model to use")
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )


class ChineseAssistantSkill(OpenAIChatSkill):
    """Skill for Chinese language assistance"""

    input_schema = ChineseAssistantInput
    output_schema = OpenAIOutput

    def __init__(self, credentials: Optional[OpenAICredentials] = None):
        super().__init__(credentials)

    def process(self, input_data: T) -> OpenAIOutput:
        # Add language check to ensure response is in Chinese
        if "你是" not in input_data.system_prompt:
            input_data.system_prompt = (
                "你是一个中文助手。" + input_data.system_prompt + "请用中文回答。"
            )

        return super().process(input_data)
