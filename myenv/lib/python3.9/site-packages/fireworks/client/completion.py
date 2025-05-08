from typing import Dict, Optional

from .api import CompletionResponse, CompletionStreamResponse
from .base_completion import BaseCompletion
from .api_client import FireworksClient


class Completion(BaseCompletion):
    """
    Class for handling text completions.
    """

    endpoint = "completions"
    response_class = CompletionResponse
    stream_response_class = CompletionStreamResponse

    @classmethod
    def _get_data_key(cls) -> str:
        return "prompt"


class CompletionV2(Completion):
    """
    Class for handling text completions.
    """

    def __init__(self, client: FireworksClient):
        self._client = client

    def create(
        self,
        model,
        prompt=None,
        request_timeout=600,
        stream=False,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        return super().create(
            model,
            prompt,
            request_timeout,
            stream=stream,
            client=self._client,
            extra_headers=extra_headers,
            **kwargs,
        )

    def acreate(
        self,
        model,
        prompt=None,
        request_timeout=600,
        stream=True,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        return super().acreate(
            model,
            prompt,
            request_timeout,
            stream=stream,
            client=self._client,
            extra_headers=extra_headers,
            **kwargs,
        )
