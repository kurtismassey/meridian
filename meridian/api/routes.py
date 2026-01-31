"""
API routes.
"""

import asyncio

from fastapi import APIRouter

from meridian.api.models import (
    ExtractBatchRequest,
    ExtractRequest,
    HealthResponse,
)
from meridian.config.logging import get_logger
from meridian.core.models import ExtractionResult
from meridian.services.extraction import get_extractor

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check service health.
    """
    return HealthResponse()


@router.post("/extract", response_model=ExtractionResult)
async def extract_entities(request: ExtractRequest) -> ExtractionResult:
    """
    Extract named entities from text.

    Identifies UK geographic and administrative entities including:
    - LOCAL_AUTHORITY: UK councils (e.g., "Manchester City Council")
    - REGION: UK regions (e.g., "North West")
    - POSTCODE_AREA: UK postcode areas (e.g., "M1", "SW1A")
    """
    extractor = get_extractor()
    result = await asyncio.to_thread(extractor.extract, request.text)
    logger.info("Extracted %d entities", len(result.entities))
    return result


@router.post("/extract/batch", response_model=list[ExtractionResult])
async def extract_entities_batch(
    request: ExtractBatchRequest,
) -> list[ExtractionResult]:
    """
    Extract named entities from multiple texts.
    """
    extractor = get_extractor()
    results = await asyncio.to_thread(extractor.extract_batch, request.texts)
    logger.info("Processed %d texts", len(results))
    return results
