from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from .skills import FireworksChatSkill, FireworksInput, FireworksOutput

# TODO: Test this thing.


class ConversationState(BaseModel):
    """Model to track conversation state"""

    messages: List[Dict[str, str]] = Field(
        default_factory=list, description="List of conversation messages"
    )
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt for the conversation",
    )
    model: str = Field(
        default="accounts/fireworks/models/deepseek-r1",
        description="Model being used for the conversation",
    )
    temperature: float = Field(default=0.7, description="Temperature setting")
    max_tokens: Optional[int] = Field(default=131072, description="Max tokens setting")


class FireworksConversationManager:
    """Manager for handling conversation state with Fireworks AI"""

    def __init__(
        self,
        skill: Optional[FireworksChatSkill] = None,
        system_prompt: str = "You are a helpful assistant.",
        model: str = "accounts/fireworks/models/deepseek-r1",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize conversation manager.

        Args:
            skill: FireworksChatSkill instance (creates new one if None)
            system_prompt: Initial system prompt
            model: Model to use
            temperature: Temperature setting
            max_tokens: Max tokens setting
        """
        self.skill = skill or FireworksChatSkill()
        self.state = ConversationState(
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def send_message(self, user_input: str) -> FireworksOutput:
        """
        Send a message and get response while maintaining conversation history.

        Args:
            user_input: User's message

        Returns:
            FireworksOutput: Model's response
        """
        # Create input with current conversation state
        input_data = FireworksInput(
            user_input=user_input,
            system_prompt=self.state.system_prompt,
            conversation_history=self.state.messages,
            model=self.state.model,
            temperature=self.state.temperature,
            max_tokens=self.state.max_tokens,
        )

        # Get response
        result = self.skill.process(input_data)

        # Update conversation history
        self.state.messages.extend(
            [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": result.response},
            ]
        )

        return result

    def reset_conversation(self) -> None:
        """Reset the conversation history while maintaining other settings"""
        self.state.messages = []

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.state.messages.copy()

    def update_system_prompt(self, new_prompt: str) -> None:
        """Update the system prompt for future messages"""
        self.state.system_prompt = new_prompt

    def save_state(self, file_path: str) -> None:
        """Save conversation state to a file"""
        with open(file_path, "w") as f:
            f.write(self.state.model_dump_json(indent=2))

    def load_state(self, file_path: str) -> None:
        """Load conversation state from a file"""
        with open(file_path, "r") as f:
            data = f.read()
            self.state = ConversationState.model_validate_json(data)
