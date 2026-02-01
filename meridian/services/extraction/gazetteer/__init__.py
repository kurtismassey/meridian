"""
Gazetteer.
"""

from meridian.services.extraction.gazetteer.loader import (
    get_local_authority_phrases,
    get_region_phrases,
    load_gazetteer,
)
from meridian.services.extraction.gazetteer.models import (
    Gazetteer,
    LocalAuthorityRow,
    RegionRow,
)
from meridian.services.extraction.gazetteer.sources import (
    ensure_data,
    fetch_onspd,
    fetch_open_names,
)

__all__ = [
    "get_local_authority_phrases",
    "get_region_phrases",
    "Gazetteer",
    "LocalAuthorityRow",
    "RegionRow",
    "load_gazetteer",
    "ensure_data",
    "fetch_onspd",
    "fetch_open_names",
]
