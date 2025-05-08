"""
Schemas for Exa Search API.

This module defines the input and output schemas for the Exa search API.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl

from airtrain.core.schemas import InputSchema, OutputSchema


class ExaContentConfig(BaseModel):
    """Configuration for the content to be returned by Exa search."""

    text: bool = Field(default=True, description="Whether to return text content.")
    extractedText: Optional[bool] = Field(
        default=None, description="Whether to return extracted text content."
    )
    embedded: Optional[bool] = Field(
        default=None, description="Whether to return embedded content."
    )
    links: Optional[bool] = Field(
        default=None, description="Whether to return links from the content."
    )
    screenshot: Optional[bool] = Field(
        default=None, description="Whether to return screenshots of the content."
    )
    highlighted: Optional[bool] = Field(
        default=None, description="Whether to return highlighted text."
    )


class ExaSearchInputSchema(InputSchema):
    """Input schema for Exa search API."""

    query: str = Field(description="The search query to execute.")
    numResults: Optional[int] = Field(
        default=None, description="Number of results to return."
    )
    contents: Optional[ExaContentConfig] = Field(
        default_factory=ExaContentConfig,
        description="Configuration for the content to be returned.",
    )
    highlights: Optional[dict] = Field(
        default=None, description="Highlighting configuration for search results."
    )
    useAutoprompt: Optional[bool] = Field(
        default=None, description="Whether to use autoprompt for the search."
    )
    type: Optional[str] = Field(default=None, description="Type of search to perform.")
    includeDomains: Optional[List[str]] = Field(
        default=None, description="List of domains to include in the search."
    )
    excludeDomains: Optional[List[str]] = Field(
        default=None, description="List of domains to exclude from the search."
    )


class ExaModerationConfig(BaseModel):
    """Moderation configuration returned in search results."""

    llamaguardS1: Optional[bool] = None
    llamaguardS3: Optional[bool] = None
    llamaguardS4: Optional[bool] = None
    llamaguardS12: Optional[bool] = None
    domainBlacklisted: Optional[bool] = None
    domainBlacklistedMedia: Optional[bool] = None


class ExaHighlight(BaseModel):
    """Highlight information for a search result."""

    text: str
    score: float


class ExaSearchResult(BaseModel):
    """Individual search result from Exa."""

    id: str
    url: str
    title: Optional[str] = None
    text: Optional[str] = None
    extractedText: Optional[str] = None
    embedded: Optional[Dict[str, Any]] = None
    score: float
    published: Optional[str] = None
    author: Optional[str] = None
    highlights: Optional[List[ExaHighlight]] = None
    robotsAllowed: Optional[bool] = None
    moderationConfig: Optional[ExaModerationConfig] = None
    urls: Optional[List[str]] = None


class ExaCostDetails(BaseModel):
    """Cost details for an Exa search request."""

    total: float
    search: Dict[str, float]
    contents: Dict[str, float]


class ExaSearchOutputSchema(OutputSchema):
    """Output schema for Exa search API."""

    results: List[ExaSearchResult] = Field(description="List of search results.")
    query: str = Field(description="The original search query.")
    autopromptString: Optional[str] = Field(
        default=None, description="Autoprompt string used for the search if enabled."
    )
    costDollars: Optional[ExaCostDetails] = Field(
        default=None, description="Cost details for the search request."
    )
