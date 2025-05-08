import os
from .completion import Completion
from .chat_completion import ChatCompletion
from .embedding import Embedding
from .rerank import Rerank
from .chat import Chat
from .model import Model
from .api_client_v2 import (
    Fireworks,
    AsyncFireworks,
)
from . import _version

__version__ = _version.get_versions()["version"]

api_key = os.environ.get("FIREWORKS_API_KEY")
base_url = os.environ.get("FIREWORKS_API_BASE", "https://api.fireworks.ai/inference/v1")

__all__ = [
    "__version__",
    "AsyncFireworks",
    "Chat",
    "ChatCompletion",
    "Completion",
    "Fireworks",
    "Model",
    "Embedding",
    "Rerank",
]
