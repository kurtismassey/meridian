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
