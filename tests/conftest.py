"""
Pytest config and shared fixtures.
"""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from api.main import app
from fastapi.testclient import TestClient
from meridian.services.extraction.gazetteer.loader import load_gazetteer

from meridian import Meridian


@pytest.fixture(autouse=True)
def _no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch ensure_data to do nothing so tests use existing CSVs without network.
    Also clear the load_gazetteer cache so each test gets a fresh load.
    """
    monkeypatch.setattr(
        "meridian.services.extraction.gazetteer.loader.ensure_data",
        lambda force=False: None,
    )
    load_gazetteer.cache_clear()


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


@pytest.fixture
def mock_data_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Patch settings.DATA_DIR across all gazetteer modules to use tmp_path.
    Yields tmp_path for test setup.
    """
    with (
        patch(
            "meridian.services.extraction.gazetteer.sources.settings"
        ) as mock_sources,
        patch("meridian.services.extraction.gazetteer.loader.settings") as mock_loader,
        patch(
            "meridian.services.extraction.gazetteer.prepare.settings"
        ) as mock_prepare,
    ):
        mock_sources.DATA_DIR = tmp_path
        mock_sources.ONSPD_EXTRACT_DIR = "onspd_extract"
        mock_loader.DATA_DIR = tmp_path
        mock_prepare.DATA_DIR = tmp_path
        mock_prepare.ONSPD_EXTRACT_DIR = "onspd_extract"
        load_gazetteer.cache_clear()
        yield tmp_path


@pytest.fixture
def mock_ensure_data() -> Generator[MagicMock, None, None]:
    """
    Patch ensure_data in loader and yield the mock.
    """
    with patch("meridian.services.extraction.gazetteer.loader.ensure_data") as mock:
        yield mock


@pytest.fixture
def mock_fetch_onspd() -> Generator[MagicMock, None, None]:
    """
    Patch fetch_onspd in sources and yield the mock.
    """
    with patch("meridian.services.extraction.gazetteer.sources.fetch_onspd") as mock:
        yield mock


@pytest.fixture
def mock_fetch_open_names() -> Generator[MagicMock, None, None]:
    """
    Patch fetch_open_names in sources and yield the mock.
    """
    with patch(
        "meridian.services.extraction.gazetteer.sources.fetch_open_names"
    ) as mock:
        yield mock


def create_test_csvs(data_dir: Path) -> None:
    """
    Create minimal test CSVs in data_dir.
    """
    (data_dir / "local_authorities.csv").write_text("name,code\nTest Council,TC1\n")
    (data_dir / "regions.csv").write_text("name,code\nTest Region,TR1\n")
