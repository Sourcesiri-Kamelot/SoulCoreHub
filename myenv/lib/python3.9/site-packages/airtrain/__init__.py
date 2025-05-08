"""
Airtrain: AI Agent Framework

This library provides a flexible framework for building AI agents
that can complete complex tasks using AI models, skills, and tools.
"""

__version__ = "0.1.68"

import sys

# Core imports
from .core import Skill, ProcessingError, InputSchema, OutputSchema, BaseCredentials

# Integration imports - Credentials
from .integrations import (
    # OpenAI
    OpenAICredentials,
    OpenAIChatSkill,
    # Anthropic
    AnthropicCredentials,
    AnthropicChatSkill,
    # Together.ai
    TogetherAICredentials,
    TogetherAIChatSkill,
    # Fireworks
    FireworksCredentials,
    FireworksChatSkill,
    # Google
    GeminiCredentials,
    GoogleChatSkill,
    # Search
    ExaCredentials,
    ExaSearchSkill,
    ExaSearchInputSchema,
    ExaSearchOutputSchema,
)

# Integration imports - Skills
from .integrations.aws.skills import AWSBedrockSkill
from .integrations.google.skills import GoogleChatSkill
from .integrations.groq.skills import GroqChatSkill
from .integrations.ollama.skills import OllamaChatSkill
from .integrations.sambanova.skills import SambanovaChatSkill
from .integrations.cerebras.skills import CerebrasChatSkill

# Tool imports
from .tools import (
    ToolFactory,
    register_tool,
    StatelessTool,
    StatefulTool,
    BaseTool,
    ListDirectoryTool,
    DirectoryTreeTool,
    ApiCallTool,
    ExecuteCommandTool,
    FindFilesTool,
    TerminalNavigationTool,
    SearchTermTool,
    RunPytestTool,
)

# Agent imports
from .agents import (
    BaseAgent,
    AgentFactory,
    register_agent,
    BaseMemory,
    ShortTermMemory,
    LongTermMemory,
    SharedMemory,
)

# Telemetry import - must be imported after version is defined
from .telemetry import telemetry
from .telemetry import PackageImportTelemetryEvent


__all__ = [
    # Core
    "Skill",
    "ProcessingError",
    "InputSchema",
    "OutputSchema",
    "BaseCredentials",
    # OpenAI Integration
    "OpenAICredentials",
    "OpenAIChatSkill",
    # Anthropic Integration
    "AnthropicCredentials",
    "AnthropicChatSkill",
    # Together Integration
    "TogetherAICredentials",
    "TogetherAIChatSkill",
    # Fireworks Integration
    "FireworksCredentials",
    "FireworksChatSkill",
    # Google Integration
    "GeminiCredentials",
    "GoogleChatSkill",
    # Search Integration
    "ExaCredentials",
    "ExaSearchSkill",
    "ExaSearchInputSchema",
    "ExaSearchOutputSchema",
    # Tools
    "ToolFactory",
    "register_tool",
    "StatelessTool",
    "StatefulTool",
    "BaseTool",
    "ListDirectoryTool",
    "DirectoryTreeTool",
    "ApiCallTool",
    "ExecuteCommandTool",
    "FindFilesTool",
    "TerminalNavigationTool",
    "SearchTermTool",
    "RunPytestTool",
    # Agents
    "BaseAgent",
    "AgentFactory",
    "register_agent",
    "BaseMemory",
    "ShortTermMemory",
    "LongTermMemory",
    "SharedMemory",
    # Telemetry - not directly exposed to users
    # but initialized at import time
]

# Capture import telemetry
try:
    telemetry.capture(
        PackageImportTelemetryEvent(
            version=__version__,
            python_version=(
                f"{sys.version_info.major}."
                f"{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
        )
    )
except Exception:
    # Silently continue if telemetry fails
    pass
