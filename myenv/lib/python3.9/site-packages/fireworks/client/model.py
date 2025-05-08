from .api_client import FireworksClient
from .api import ListModelsResponse


class Model:
    @classmethod
    def list(cls, request_timeout=60):
        """Returns a list of available models.

        Args:
          request_timeout (int, optional): The request timeout in seconds. Default is 60.

        Returns:
          ListModelsResponse: A list of available models.
        """
        client = FireworksClient(request_timeout=request_timeout)
        response = client._get_request(f"{client.base_url}/models")
        return ListModelsResponse(**response)
