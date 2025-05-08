from typing import Optional, Type, List
import json
from pydantic import BaseModel
from .api_client import FireworksClient
from .error import InvalidRequestError
from .api import RerankResponse


class Rerank:
    """
    Base class for handling reranking, both synchronously and asynchronously

    Attributes:
      endpoint (str): API endpoint for the completion request.
      response_class (Type): Class used for parsing the non-streaming response.
    """

    endpoint = "rerank"  # Matching the API reference
    response_class = RerankResponse

    @classmethod
    def create(
        cls,
        model,
        query,
        documents: List[str],
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        **kwargs,
    ):
        """
        Create a completion or chat completion.

        Args:
          model (str): Model name to use for the completion.
          input (str): The input string for embedding.
          request_timeout (int, optional): Request timeout in seconds. Defaults to 600.
          **kwargs: Additional keyword arguments.

        Returns:
          RerankResponse: results of reranking, with a relevant score for each document
        """
        kwargs["query"] = query
        kwargs["documents"] = documents
        return cls._create_non_streaming(
            model, request_timeout, client=client, **kwargs
        )

    @classmethod
    def acreate(
        cls,
        model,
        query,
        documents: List[str],
        request_timeout=600,
        client: Optional[FireworksClient] = None,
        **kwargs,
    ):
        """
        Asynchronously create a completion.

        Args:
          model (str): Model name to use for the completion.
          query (str): The input query string.
          documents (List(str)): The input string for documents.
          request_timeout (int, optional): Request timeout in seconds. Defaults to 600.
          **kwargs: Additional keyword arguments.

        Returns:
          AsyncGenerator[RerankResponse]: results of reranking, with a relevant score for each document
        """
        kwargs["query"] = query
        kwargs["documents"] = documents
        return cls._acreate_non_streaming(
            model, request_timeout, client=client, **kwargs
        )

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

        print(f"{client.base_url}/{cls.endpoint}", data)
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
        data = {"model": model, **kwargs}
        response = await client.post_request_async_non_streaming(
            f"{client.base_url}/{cls.endpoint}", data=data
        )
        return cls.response_class(**response)


class RerankV1(Rerank):
    def __init__(self, client: FireworksClient):
        self._client = client

    def create(
        self,
        model,
        query: str,
        documents: List[str],
        request_timeout=600,
        **kwargs,
    ):
        return super().create(
            model,
            query,
            documents,
            request_timeout,
            client=self._client,
            **kwargs,
        )

    def acreate(
        self,
        model,
        query: str,
        documents: List[str],
        request_timeout=600,
        **kwargs,
    ):
        return super().acreate(
            model,
            query,
            documents,
            request_timeout,
            client=self._client,
            **kwargs,
        )
