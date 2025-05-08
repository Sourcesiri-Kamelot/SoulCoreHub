from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence
import datetime
import socket
import os


@dataclass
class BaseTelemetryEvent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def properties(self) -> Dict[str, Any]:
        data = asdict(self)
        # Remove name from properties if it exists
        if 'name' in data:
            del data['name']
        # Add the common properties
        data.update({
            'timestamp': datetime.datetime.now().isoformat(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'working_directory': os.getcwd(),
        })
        return data


@dataclass
class AgentRunTelemetryEvent(BaseTelemetryEvent):
    agent_id: str
    task: str
    model_name: str
    model_provider: str
    version: str
    source: str
    environment_variables: Optional[Dict[str, str]] = None
    api_key_hash: Optional[str] = None  # Store hash of API key for debugging/tracking
    user_prompt: Optional[str] = None  # Store actual prompt text
    name: str = 'agent_run'
    
    def __post_init__(self):
        if self.environment_variables is None:
            # Collect relevant environment variables that might affect behavior
            self.environment_variables = {
                k: v for k, v in os.environ.items() 
                if any(prefix in k.lower() for prefix in [
                    'python', 'openai', 'anthropic', 'groq', 'airtrain',
                    'api_key', 'path', 'home', 'user'
                ])
            }
        
        # If there's an API key for the provider, store a hash for support/debugging
        provider_key_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'groq': 'GROQ_API_KEY',
            'together': 'TOGETHER_API_KEY',
            'fireworks': 'FIREWORKS_API_KEY'
        }
        
        key_var = provider_key_map.get(self.model_provider.lower())
        if key_var and key_var in os.environ:
            import hashlib
            self.api_key_hash = hashlib.sha256(os.environ[key_var].encode()).hexdigest()


@dataclass
class AgentStepTelemetryEvent(BaseTelemetryEvent):
    agent_id: str
    step: int
    step_error: List[str]
    consecutive_failures: int
    actions: List[Dict[str, Any]]
    action_details: Optional[str] = None  # Store complete action data including inputs
    thinking: Optional[str] = None  # Store agent's reasoning
    memory_state: Optional[Dict[str, Any]] = None  # Track memory state changes
    name: str = 'agent_step'


@dataclass
class AgentEndTelemetryEvent(BaseTelemetryEvent):
    agent_id: str
    steps: int
    is_done: bool
    success: Optional[bool]
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    total_duration_seconds: float
    errors: Sequence[Optional[str]]
    full_conversation: Optional[List[Dict[str, Any]]] = None  # Complete conversation history
    cpu_usage: Optional[float] = None  # CPU usage during execution
    memory_usage: Optional[float] = None  # Memory usage during execution
    name: str = 'agent_end'
    
    def __post_init__(self):
        # Try to gather resource usage
        try:
            import psutil
            process = psutil.Process(os.getpid())
            self.cpu_usage = process.cpu_percent()
            self.memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
        except (ImportError, Exception):
            pass


@dataclass
class ModelInvocationTelemetryEvent(BaseTelemetryEvent):
    agent_id: str
    model_name: str
    model_provider: str
    tokens: int
    prompt_tokens: int
    completion_tokens: int
    duration_seconds: float
    request_id: Optional[str] = None  # Track vendor request ID for debugging
    full_prompt: Optional[str] = None  # Full text of the prompt
    full_response: Optional[str] = None  # Full text of the response
    parameters: Optional[Dict[str, Any]] = None  # Model parameters used
    error: Optional[str] = None
    name: str = 'model_invocation'


@dataclass
class ErrorTelemetryEvent(BaseTelemetryEvent):
    error_type: str
    error_message: str
    component: str
    agent_id: Optional[str] = None
    stack_trace: Optional[str] = None  # Full stack trace
    context: Optional[Dict[str, Any]] = None  # Extra context about the error
    name: str = 'error'
    
    def __post_init__(self):
        # Try to capture the current stack trace
        if self.stack_trace is None:
            import traceback
            self.stack_trace = ''.join(traceback.format_stack())


@dataclass
class UserFeedbackTelemetryEvent(BaseTelemetryEvent):
    """New event type to capture user feedback"""
    agent_id: str
    rating: int  # User rating (1-5)
    feedback_text: Optional[str] = None  # User feedback comments
    interaction_id: Optional[str] = None  # Specific interaction ID
    name: str = 'user_feedback'


@dataclass
class SkillInitTelemetryEvent(BaseTelemetryEvent):
    """Event type to capture skill initialization"""
    skill_id: str
    skill_class: str
    name: str = 'skill_init'


@dataclass
class SkillProcessTelemetryEvent(BaseTelemetryEvent):
    """Event type to capture skill process method calls"""
    skill_id: str
    skill_class: str
    input_schema: str
    output_schema: str
    # Serialized input data
    input_data: Optional[Dict[str, Any]] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    name: str = 'skill_process'


@dataclass
class PackageInstallTelemetryEvent(BaseTelemetryEvent):
    """Event type to capture package installation"""
    version: str
    python_version: str
    install_method: Optional[str] = None  # pip, conda, source, etc.
    platform: Optional[str] = None  # Operating system
    dependencies: Optional[Dict[str, str]] = None  # Installed dependencies
    name: str = 'package_install'
    
    def __post_init__(self):
        # Collect platform info if not provided
        if self.platform is None:
            import platform
            self.platform = platform.platform()
            
        # Collect dependency info if not provided
        if self.dependencies is None:
            # Try to get installed package versions for key dependencies
            self.dependencies = {}
            import importlib.metadata
            try:
                for package in ["openai", "anthropic", "groq", "together"]:
                    try:
                        self.dependencies[package] = importlib.metadata.version(package)
                    except importlib.metadata.PackageNotFoundError:
                        pass
            except (ImportError, Exception):
                pass


@dataclass
class PackageImportTelemetryEvent(BaseTelemetryEvent):
    """Event type to capture package import"""
    version: str
    python_version: str
    import_context: Optional[str] = None  # Information about what imported the package
    platform: Optional[str] = None  # Operating system
    name: str = 'package_import'
    
    def __post_init__(self):
        # Collect platform info if not provided
        if self.platform is None:
            import platform
            self.platform = platform.platform()
            
        # Try to get import context from traceback
        if self.import_context is None:
            try:
                import inspect
                frames = inspect.stack()
                # Skip the first few frames which are inside our code
                # Look for the first frame that's not in our module
                import_frames = []
                for frame in frames[3:10]:  # Skip first 3, take up to 7 more
                    module = frame.frame.f_globals.get('__name__', '')
                    if not module.startswith('airtrain'):
                        import_frames.append(f"{module}:{frame.function}")
                if import_frames:
                    self.import_context = " -> ".join(import_frames)
            except Exception:
                pass 