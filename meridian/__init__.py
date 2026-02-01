"""
Meridian: UK location NER (local authority, region, postcode).

Usage:
    from meridian import Meridian

    meridian = Meridian()
    result = meridian.recognise("Contact Manchester City Council")
    for entity in result.entities:
        print(entity.label, entity.text)

Labels and results:
    from meridian import MeridianLabel, RecogniseEntity, RecogniseResult
    MeridianLabel.REGION  # etc.
    result: RecogniseResult = meridian.recognise(...)
"""

from meridian.core.models import (
    MeridianLabel,
    RecogniseEntity,
    RecogniseResult,
)
from meridian.meridian import Meridian

__all__ = [
    "Meridian",
    "MeridianLabel",
    "RecogniseEntity",
    "RecogniseResult",
]
