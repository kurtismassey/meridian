"""
API models.
"""

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    """
    Request body for entity extraction.
    """

    text: str = Field(description="Text to extract entities from")


class ExtractBatchRequest(BaseModel):
    """
    Request body for batch entity extraction.
    """

    texts: list[str] = Field(description="List of texts to extract entities from")


class HealthResponse(BaseModel):
    """
    Health check response.
    """

    status: str = Field(default="healthy")
    version: str = Field(default="0.1.0")
