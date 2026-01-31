"""
Models for Meridian NER.
"""

from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    """
    Extracted named entity.
    """

    text: str = Field(description="The entity text as it appears in the source text")
    label: str = Field(description="Entity type label")
    start: int = Field(description="Start character position")
    end: int = Field(description="End character position")


class ExtractionResult(BaseModel):
    """
    Result of entity extraction from text.
    """

    text: str = Field(description="Original input text")
    entities: list[ExtractedEntity] = Field(default_factory=list)


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
