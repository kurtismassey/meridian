"""
API routes.
"""

import asyncio

from fastapi import APIRouter, Request
from meridian.config.logging import get_logger
from meridian.core.models import RecogniseResult

from api.models import (
    HealthResponse,
    RecogniseBatchRequest,
    RecogniseRequest,
)
from meridian import Meridian

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check service health.
    """
    return HealthResponse()


@router.post("/recognise", response_model=RecogniseResult)
async def recognise_entities(
    request: RecogniseRequest, req: Request
) -> RecogniseResult:
    """
    Recognise location entities in text.

    Identifies UK geographic and administrative entities including:
    - LOCAL_AUTHORITY: UK councils (e.g., "Manchester City Council")
    - REGION: UK regions (e.g., "North West")
    - POSTCODE_AREA: UK postcode areas (e.g., "M1", "SW1A")
    """
    meridian: Meridian = req.app.state.meridian
    result = await asyncio.to_thread(meridian.recognise, request.text)
    logger.info("Recognised %d entities", len(result.entities))
    return result


@router.post("/recognise/batch", response_model=list[RecogniseResult])
async def recognise_batch(
    request: RecogniseBatchRequest,
    req: Request,
) -> list[RecogniseResult]:
    """
    Recognise location entities in multiple texts.
    """
    meridian: Meridian = req.app.state.meridian
    results = await asyncio.to_thread(meridian.recognise_batch, request.texts)
    logger.info("Processed %d texts", len(results))
    return results
