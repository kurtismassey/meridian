"""
Pytest config and shared fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from meridian.main import app
from meridian.services.extraction import EntityExtractor


@pytest.fixture
def extractor() -> EntityExtractor:
    """
    EntityExtractor instance.
    """
    return EntityExtractor()


@pytest.fixture
def client() -> TestClient:
    """
    FastAPI test client.
    """
    return TestClient(app)
