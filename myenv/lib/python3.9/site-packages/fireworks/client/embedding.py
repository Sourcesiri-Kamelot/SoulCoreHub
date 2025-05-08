from typing import Optional, Type
import json
from pydantic import BaseModel
from .api_client import FireworksClient
from .error import InvalidRequestError
from .api import EmbeddingResponse


class Embedding:
    """
    Base class for handling embeddings. This class provides logic for creating embedding
    both synchronously and asynchronously.

    Attributes:
      endpoint (str): API endpoint for the completion request.
      response_class (Type): Class used for parsing the non-streaming response.
    """

    endpoint = "embeddings"  # Matching the API reference
    response_class = EmbeddingResponse

    @classmethod
    def create(
        cls,
        model,
        input=None,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        **kwargs,
    ):
        """
        Create an embedding response

        Args:
          model (str): Model name to use for the completion.
          input (str): The input string for embedding.
          request_timeout (int, optional): Request timeout in seconds. Defaults to 600.
          **kwargs: Additional keyword arguments.

        Returns:
          EmbeddingResponse: response for embedding request
        """
        data_key = cls._get_data_key()
        if input:
            kwargs[data_key] = input

        cls._validate_kwargs(kwargs)

        return cls._create_non_streaming(
            model, request_timeout, client=client, **kwargs
        )

    @classmethod
    def acreate(
        cls,
        model,
        input=None,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        **kwargs,
    ):
        """
        Asynchronously create a completion.

        Args:
        Create an embedding response

        Args:
          model (str): Model name to use for the completion.
          input (str): The input string for embedding.
          request_timeout (int, optional): Request timeout in seconds. Defaults to 600.
          **kwargs: Additional keyword arguments.

        Returns:
          AsyncGenerator[EmbeddingResponse]: async response for embedding request
        """
        data_key = cls._get_data_key()
        if input:
            kwargs[data_key] = input
        cls._validate_kwargs(kwargs)

        return cls._acreate_non_streaming(
            model, request_timeout, client=client, **kwargs
        )

    @classmethod
    def _validate_kwargs(cls, kwargs):
        assert cls._get_data_key() in kwargs, f"{cls._get_data_key()} must be provided"

    @classmethod
    def _get_data_key(cls) -> str:
        return "input"

    @classmethod
    def _create_non_streaming(
        cls,
        model: str,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        **kwargs,
    ):
        client = client or FireworksClient(request_timeout=request_timeout)
        data = {"model": model, **kwargs}
        response = client.post_request_non_streaming(
            f"{client.base_url}/{cls.endpoint}", data=data
        )
        return cls.response_class(**response)

    @classmethod
    async def _acreate_non_streaming(
        cls,
        model: str,
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        **kwargs,
    ):
        client = client or FireworksClient(request_timeout=request_timeout)
        data = {"model": model, "stream": False, **kwargs}
        response = await client.post_request_async_non_streaming(
            f"{client.base_url}/{cls.endpoint}", data=data
        )
        return cls.response_class(**response)


class EmbeddingV1(Embedding):
    def __init__(self, client: FireworksClient):
        self._client = client

    def create(
        self,
        model,
        input=None,
        request_timeout=600,
        **kwargs,
    ):
        return super().create(
            model,
            input,
            request_timeout,
            client=self._client,
            **kwargs,
        )

    def acreate(
        self,
        model,
        input=None,
        request_timeout=600,
        **kwargs,
    ):
        return super().acreate(
            model,
            input,
            request_timeout,
            client=self._client,
            **kwargs,
        )
