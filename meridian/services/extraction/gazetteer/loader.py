"""
Load gazetteer data.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

from meridian.config.settings import settings
from meridian.services.extraction.gazetteer.models import (
    Gazetteer,
    LocalAuthorityRow,
    RegionRow,
)
from meridian.services.extraction.gazetteer.sources import ensure_data

LOCAL_AUTHORITIES_FILE = "local_authorities.csv"
REGIONS_FILE = "regions.csv"


def _dataframe_to_local_authorities(df: pd.DataFrame) -> tuple[LocalAuthorityRow, ...]:
    """
    Validate DataFrame columns (name, code) into LocalAuthorityRow tuple.
    """
    df = df.astype(str).fillna("")
    df["code"] = df["code"].replace("", None)
    return tuple(LocalAuthorityRow.model_validate(row) for row in df.to_dict("records"))


def _dataframe_to_regions(df: pd.DataFrame) -> tuple[RegionRow, ...]:
    """
    Validate DataFrame columns (name, code) into RegionRow tuple.
    """
    df = df.astype(str).fillna("")
    df["code"] = df["code"].replace("", None)
    return tuple(RegionRow.model_validate(row) for row in df.to_dict("records"))


def _load_local_authorities(path: Path) -> tuple[LocalAuthorityRow, ...]:
    """
    Load and validate local authority rows from CSV path.
    """
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return _dataframe_to_local_authorities(df)


def _load_regions(path: Path) -> tuple[RegionRow, ...]:
    """
    Load and validate region rows from CSV path.
    """
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return _dataframe_to_regions(df)


@lru_cache(maxsize=1)
def load_gazetteer() -> Gazetteer:
    """
    Load local authorities and regions from CSVs.

    Ensures data is fetched once, then loads both files. Result is cached.
    """
    ensure_data()
    la_path = settings.DATA_DIR / LOCAL_AUTHORITIES_FILE
    rgn_path = settings.DATA_DIR / REGIONS_FILE
    return Gazetteer(
        local_authorities=_load_local_authorities(la_path),
        regions=_load_regions(rgn_path),
    )


def get_local_authority_phrases() -> tuple[str, ...]:
    """
    Local authority names for PhraseMatcher.
    """
    return tuple(row.name for row in load_gazetteer().local_authorities)


def get_region_phrases() -> tuple[str, ...]:
    """
    Region names for PhraseMatcher.
    """
    return tuple(row.name for row in load_gazetteer().regions)
