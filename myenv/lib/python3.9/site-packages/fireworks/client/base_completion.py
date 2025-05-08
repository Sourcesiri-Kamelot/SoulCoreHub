from typing import Dict, Optional, Type
import json
from pydantic import BaseModel
from .api_client import FireworksClient
from .error import InvalidRequestError


# Parse the server side events
def _parse_sse(lines, resp_type: BaseModel):
    for line in lines:
        if line and line != "[DONE]":
            data = json.loads(line)
            yield resp_type(**data)


async def _parse_sse_async(lines, resp_type: BaseModel):
    async for line in lines:
        if line and line != "[DONE]":
            data = json.loads(line)
            yield resp_type(**data)


class BaseCompletion:
    """
    Base class for handling completions. This class provides shared logic for creating completions,
    both synchronously and asynchronously, and both streaming and non-streaming.

    Attributes:
      endpoint (str): API endpoint for the completion request.
      response_class (Type): Class used for parsing the non-streaming response.
      stream_response_class (Type): Class used for parsing the streaming response.
    """

    endpoint = ""
    response_class: Type = None
    stream_response_class: Type = None

    @classmethod
    def create(
        cls,
        model,
        prompt_or_messages=None,
        request_timeout=600,
        stream=False,
        client: Optional[FireworksClient] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        Create a completion or chat completion.

        Args:
          model (str): Model name to use for the completion.
          prompt_or_messages (Union[str, List[ChatMessage]]): The prompt for Completion or a list of chat messages for ChatCompletion. If not specified, must specify either `prompt` or `messages` in kwargs.
          request_timeout (int, optional): Request timeout in seconds. Defaults to 600.
          stream (bool, optional): Whether to use streaming or not. Defaults to False.
          **kwargs: Additional keyword arguments.

        Returns:
          Union[CompletionResponse, Generator[CompletionStreamResponse, None, None]]:
            Depending on the `stream` argument, either returns a CompletionResponse
            or a generator yielding CompletionStreamResponse.
        """
        data_key = cls._get_data_key()
        if prompt_or_messages:
            kwargs[data_key] = prompt_or_messages

        cls._validate_kwargs(kwargs)

        if not isinstance(stream, bool):
            raise InvalidRequestError("stream value is not a valid boolean")
        if stream:
            return cls._create_streaming(
                model,
                request_timeout,
                client=client,
                extra_headers=extra_headers,
                **kwargs,
            )
        else:
            return cls._create_non_streaming(
                model,
                request_timeout,
                client=client,
                extra_headers=extra_headers,
                **kwargs,
            )

    @classmethod
    def acreate(
        cls,
        model,
        prompt_or_messages=None,
        request_timeout=600,
        stream=False,
        client: Optional[FireworksClient] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        Asynchronously create a completion.

        Args:
          model (str): Model name to use for the completion.
          request_timeout (int, optional): Request timeout in seconds. Defaults to 600.
          stream (bool, optional): Whether to use streaming or not. Defaults to False.
          **kwargs: Additional keyword arguments.

        Returns:
          Union[CompletionResponse, AsyncGenerator[CompletionStreamResponse, None]]:
            Depending on the `stream` argument, either returns a CompletionResponse or an async generator yielding CompletionStreamResponse.
        """
        data_key = cls._get_data_key()
        if prompt_or_messages:
            kwargs[data_key] = prompt_or_messages
        cls._validate_kwargs(kwargs)
        if not isinstance(stream, bool):
            raise InvalidRequestError("stream value is not a valid boolean")
        if stream:
            return cls._acreate_streaming(
                model,
                request_timeout,
                client=client,
                extra_headers=extra_headers,
                **kwargs,
            )
        else:
            return cls._acreate_non_streaming(
                model,
                request_timeout,
                client=client,
                extra_headers=extra_headers,
                **kwargs,
            )

    @classmethod
    def _validate_kwargs(cls, kwargs):
        assert cls._get_data_key() in kwargs, f"{cls._get_data_key()} must be provided"

    @classmethod
    def _get_data_key(cls) -> str:
        """
        Get the key used for the main data (e.g., "prompt" or "messages").
        This method should be overridden by derived classes to return the appropriate key.
        """
        raise NotImplementedError(
            "Derived classes should implement this method to return the appropriate data key"
        )

    @classmethod
    def _create_streaming(
        cls,
        model: str,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        client = client or FireworksClient(request_timeout=request_timeout)
        data = {"model": model, "stream": True, **kwargs}
        response = client.post_request_streaming(
            f"{client.base_url}/{cls.endpoint}",
            data=data,
            extra_headers=extra_headers,
        )
        for event in _parse_sse(response, cls.stream_response_class):
            yield event

    @classmethod
    def _create_non_streaming(
        cls,
        model: str,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        client = client or FireworksClient(request_timeout=request_timeout)
        data = {"model": model, "stream": False, **kwargs}
        response = client.post_request_non_streaming(
            f"{client.base_url}/{cls.endpoint}",
            data=data,
            extra_headers=extra_headers,
        )
        return cls.response_class(**response)

    @classmethod
    async def _acreate_streaming(
        cls,
        model: str,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        client = client or FireworksClient(request_timeout=request_timeout)
        data = {"model": model, "stream": True, **kwargs}
        response = client.post_request_async_streaming(
            f"{client.base_url}/{cls.endpoint}",
            data=data,
            extra_headers=extra_headers,
        )
        async for event in _parse_sse_async(response, cls.stream_response_class):
            yield event

    @classmethod
    async def _acreate_non_streaming(
        cls,
        model: str,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        client = client or FireworksClient(request_timeout=request_timeout)
        data = {"model": model, "stream": False, **kwargs}
        response = await client.post_request_async_non_streaming(
            f"{client.base_url}/{cls.endpoint}",
            data=data,
            extra_headers=extra_headers,
        )
        return cls.response_class(**response)
