"""
Skills for Exa Search API.

This module provides skills for using the Exa search API.
"""

import json
import logging
import httpx
from typing import Optional, Dict, Any, List, cast

from pydantic import ValidationError

from airtrain.core.skills import Skill, ProcessingError
from .credentials import ExaCredentials
from .schemas import ExaSearchInputSchema, ExaSearchOutputSchema, ExaSearchResult


logger = logging.getLogger(__name__)


class ExaSearchSkill(Skill[ExaSearchInputSchema, ExaSearchOutputSchema]):
    """Skill for searching the web using the Exa search API."""

    input_schema = ExaSearchInputSchema
    output_schema = ExaSearchOutputSchema

    EXA_API_ENDPOINT = "https://api.exa.ai/search"

    def __init__(
        self,
        credentials: ExaCredentials,
        timeout: float = 60.0,
        max_retries: int = 3,
        **kwargs,
    ):
        """
        Initialize the Exa search skill.

        Args:
            credentials: Credentials for accessing the Exa API
            timeout: Timeout for API requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        super().__init__(**kwargs)
        self.credentials = credentials
        self.timeout = timeout
        self.max_retries = max_retries

    async def process(self, input_data: ExaSearchInputSchema) -> ExaSearchOutputSchema:
        """
        Process a search request using the Exa API.

        Args:
            input_data: Search input parameters

        Returns:
            Search results from Exa

        Raises:
            ProcessingError: If there's an issue with the API request
        """
        try:
            # Prepare request payload
            payload = input_data.model_dump(exclude_none=True)

            # Build request headers
            headers = {
                "content-type": "application/json",
                "Authorization": f"Bearer {self.credentials.api_key.get_secret_value()}",
            }

            # Make the API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.EXA_API_ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )

                # Check for successful response
                if response.status_code == 200:
                    result_data = response.json()

                    # Construct the output schema
                    output = ExaSearchOutputSchema(
                        results=result_data.get("results", []),
                        query=input_data.query,
                        autopromptString=result_data.get("autopromptString"),
                        costDollars=result_data.get("costDollars"),
                    )

                    return output
                else:
                    # Handle error responses
                    error_message = f"Exa API returned status code {response.status_code}: {response.text}"
                    logger.error(error_message)
                    raise ProcessingError(error_message)

        except httpx.TimeoutException:
            error_message = f"Timeout while querying Exa API (timeout={self.timeout}s)"
            logger.error(error_message)
            raise ProcessingError(error_message)

        except ValidationError as e:
            error_message = f"Schema validation error: {str(e)}"
            logger.error(error_message)
            raise ProcessingError(error_message)

        except Exception as e:
            error_message = f"Unexpected error while querying Exa API: {str(e)}"
            logger.error(error_message)
            raise ProcessingError(error_message)
