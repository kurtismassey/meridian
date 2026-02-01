"""
Models for Meridian NER.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class MeridianLabel(StrEnum):
    """
    Entity labels.
    """

    LOCAL_AUTHORITY = "LOCAL_AUTHORITY"
    REGION = "REGION"
    POSTCODE_AREA = "POSTCODE_AREA"


class RecogniseEntity(BaseModel):
    """
    Named entity recognised from text.
    """

    text: str = Field(description="The entity text as it appears in the source text")
    label: MeridianLabel = Field(description="Entity type label")
    start: int = Field(description="Start character position")
    end: int = Field(description="End character position")


class RecogniseResult(BaseModel):
    """
    Result of recognising location entities in text.
    """

    text: str = Field(description="Original input text")
    entities: list[RecogniseEntity] = Field(default_factory=list)
