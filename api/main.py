"""
Meridian API.
"""

import logging
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from meridian.config.logging import get_logger, setup_logging

from api.routes import router
from meridian import Meridian

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise."""
    setup_logging()
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    app.state.meridian = Meridian(model_path="models/meridian-ner")
    logger.info("Meridian API started")
    yield
    logger.info("Meridian API stopped")


app = FastAPI(
    title="Meridian",
    description="Meridian API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """
    Log requests.
    """
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s %d %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
    )
    return response


app.include_router(router)
