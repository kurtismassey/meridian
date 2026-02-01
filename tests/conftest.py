"""
Pytest config and shared fixtures.
"""

import pytest
from api.main import app
from fastapi.testclient import TestClient

from meridian import Meridian


@pytest.fixture
def meridian() -> Meridian:
    """
    Meridian instance for extraction tests.
    """
    return Meridian()


@pytest.fixture
def client() -> TestClient:
    """
    FastAPI test client (app.state.meridian set so routes work without lifespan).
    """
    app.state.meridian = Meridian()
    return TestClient(app)
