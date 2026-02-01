"""
Gazetteer models.
"""

from pydantic import BaseModel, Field


class LocalAuthorityRow(BaseModel):
    """
    One row from local_authorities.csv.
    """

    name: str = Field(description="Local authority name (e.g. Manchester City Council)")
    code: str | None = Field(default=None, description="GSS / ONS code")


class RegionRow(BaseModel):
    """
    One row from regions.csv.
    """

    name: str = Field(description="Region name (e.g. North West)")
    code: str | None = Field(default=None, description="GSS / NUTS code")


class Gazetteer(BaseModel):
    """
    Loaded local authorities and regions from gazetteer CSVs.
    """

    local_authorities: tuple[LocalAuthorityRow, ...] = Field(
        default_factory=tuple,
        description="Local authority rows",
    )
    regions: tuple[RegionRow, ...] = Field(
        default_factory=tuple,
        description="Region rows",
    )
