from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from airtrain.integrations.fireworks.skills import FireworksChatSkill, FireworksInput
from airtrain.core.skills import ProcessingError
import json


class AgentSpecification(BaseModel):
    """Model to capture agent specifications"""

    name: str = Field(..., description="Name of the agent")
    purpose: str = Field(..., description="Primary purpose of the agent")
    input_type: str = Field(..., description="Type of input the agent accepts")
    output_type: str = Field(..., description="Type of output the agent produces")
    required_skills: List[str] = Field(
        default_factory=list, description="Skills required by the agent"
    )
    conversation_style: str = Field(
        ..., description="Style of conversation (formal, casual, technical, etc.)"
    )
    safety_constraints: List[str] = Field(
        default_factory=list, description="Safety constraints for the agent"
    )
    reasoning: Optional[str] = Field(
        None, description="Reasoning behind agent design decisions"
    )


class AgentBuilder:
    """AI-powered agent builder"""

    def __init__(self):
        self.skill = FireworksChatSkill()
        self.system_prompt = """You are an expert AI Agent architect. Your role is to help users build AI agents by:
1. Understanding their requirements through targeted questions
2. Designing appropriate agent architectures
3. Selecting optimal skills and models
4. Ensuring safety and ethical constraints
5. Providing clear reasoning for all decisions

Ask one question at a time. Wait for user response before proceeding.
Start by asking about the primary purpose of the agent they want to build.

Your responses must be in this format:
QUESTION: [Your question here]
CONTEXT: [Brief context about why this question is important]

When creating the final specification, output valid JSON matching the AgentSpecification schema."""

    def _get_next_question(self, conversation_history: List[Dict[str, str]]) -> str:
        input_data = FireworksInput(
            user_input="Based on the conversation so far, what's the next question to ask?",
            system_prompt=self.system_prompt,
            model="accounts/fireworks/models/deepseek-r1",
            temperature=0.7,
            conversation_history=conversation_history,
        )

        try:
            result = self.skill.process(input_data)
            return result.response
        except Exception as e:
            raise ProcessingError(f"Failed to generate next question: {str(e)}")

    def _create_specification(
        self, conversation_history: List[Dict[str, str]]
    ) -> AgentSpecification:
        input_data = FireworksInput(
            user_input="Based on our conversation, create a complete agent specification in valid JSON format.",
            system_prompt=self.system_prompt,
            model="accounts/fireworks/models/deepseek-r1",
            temperature=0.7,
            conversation_history=conversation_history,
        )

        result = self.skill.process(input_data)

        try:
            # Extract JSON from the response (it might be wrapped in markdown or other text)
            json_str = result.response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            return AgentSpecification.model_validate_json(json_str)
        except Exception as e:
            raise ProcessingError(f"Failed to parse agent specification: {str(e)}")

    def build_agent(self) -> AgentSpecification:
        conversation_history = []

        print("\nWelcome to the AI Agent Builder!")
        print("I'll help you create a custom AI agent through a series of questions.\n")

        while True:
            next_question = self._get_next_question(conversation_history)
            print(f"\n{next_question}")

            user_input = input("\nYour response (type 'done' when finished): ").strip()

            if user_input.lower() == "done":
                if len(conversation_history) < 6:  # Minimum questions needed
                    print(
                        "\nPlease answer a few more questions to create a complete specification."
                    )
                    continue
                try:
                    return self._create_specification(conversation_history)
                except ProcessingError as e:
                    print(f"\nError creating specification: {str(e)}")
                    print(
                        "Let's continue with a few more questions to gather complete information."
                    )
                    continue

            conversation_history.extend(
                [
                    {"role": "assistant", "content": next_question},
                    {"role": "user", "content": user_input},
                ]
            )
