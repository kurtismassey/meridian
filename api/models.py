"""
API models.
"""

from pydantic import BaseModel, Field


class RecogniseRequest(BaseModel):
    """
    Request body for entity recognition.
    """

    text: str = Field(description="Text to recognise location entities in")


class RecogniseBatchRequest(BaseModel):
    """
    Request body for batch entity recognition.
    """

    texts: list[str] = Field(
        description="List of texts to recognise location entities in"
    )


class HealthResponse(BaseModel):
    """
    Health check response.
    """

    status: str = Field(default="healthy")
    version: str = Field(default="0.1.0")
