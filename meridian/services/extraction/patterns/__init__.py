"""
Extraction patterns.
"""

from meridian.services.extraction.patterns.postcode import (
    POSTCODE_OUTCODE_PATTERN,
    find_postcode_matches,
)

__all__ = ["POSTCODE_OUTCODE_PATTERN", "find_postcode_matches"]
