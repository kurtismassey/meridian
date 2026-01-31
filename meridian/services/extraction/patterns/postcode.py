"""
UK postcode pattern for POSTCODE_AREA extraction.
"""

import re

# UK postcode outcode: 1–2 letters + 1–2 digits + optional letter (e.g. M4, SW1, SW1A)
POSTCODE_OUTCODE_PATTERN = re.compile(
    r"\b([A-Z]{1,2}[0-9][0-9A-Z]?)(?:\s+[0-9][A-Z]{2})?\b",
    re.IGNORECASE,
)


def find_postcode_matches(text: str) -> list[tuple[int, int]]:
    """
    Find UK postcode outcode character ranges in text.

    Returns (start_char, end_char) for each outcode (group 1 of the pattern).
    """
    return [(m.start(1), m.end(1)) for m in POSTCODE_OUTCODE_PATTERN.finditer(text)]
