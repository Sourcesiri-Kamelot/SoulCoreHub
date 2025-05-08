"""
Airtrain Telemetry

This package provides telemetry functionality for Airtrain usage.
Telemetry is enabled by default to help improve the library and can be disabled by 
setting AIRTRAIN_TELEMETRY_ENABLED=false in your environment variables or .env file.
"""

from airtrain.telemetry.service import ProductTelemetry
from airtrain.telemetry.views import (
    AgentRunTelemetryEvent,
    AgentStepTelemetryEvent,
    AgentEndTelemetryEvent,
    ModelInvocationTelemetryEvent,
    ErrorTelemetryEvent,
    UserFeedbackTelemetryEvent,
    SkillInitTelemetryEvent,
    SkillProcessTelemetryEvent,
    PackageInstallTelemetryEvent,
    PackageImportTelemetryEvent,
)

__all__ = [
    "ProductTelemetry",
    "AgentRunTelemetryEvent",
    "AgentStepTelemetryEvent",
    "AgentEndTelemetryEvent",
    "ModelInvocationTelemetryEvent",
    "ErrorTelemetryEvent",
    "UserFeedbackTelemetryEvent",
    "SkillInitTelemetryEvent",
    "SkillProcessTelemetryEvent",
    "PackageInstallTelemetryEvent",
    "PackageImportTelemetryEvent",
]

# Create a singleton instance for easy import
telemetry = ProductTelemetry() 