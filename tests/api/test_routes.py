"""
Tests for Meridian API endpoints.
"""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """
    Tests for health check endpoint.
    """

    def test_health_returns_200(self, client: TestClient) -> None:
        """
        Health endpoint should return 200.
        """
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client: TestClient) -> None:
        """
        Health endpoint should return healthy status.
        """
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"


class TestExtractEndpoint:
    """
    Tests for extract endpoint.
    """

    def test_extract_returns_200(self, client: TestClient) -> None:
        """
        Extract endpoint should return 200 for valid request.
        """
        response = client.post("/extract", json={"text": "Hey Meridian"})
        assert response.status_code == 200

    def test_extract_returns_text(self, client: TestClient) -> None:
        """
        Extract endpoint should return the original text.
        """
        response = client.post("/extract", json={"text": "Test input"})
        data = response.json()
        assert data["text"] == "Test input"

    def test_extract_returns_entities_list(self, client: TestClient) -> None:
        """
        Extract endpoint should return entities list.
        """
        response = client.post("/extract", json={"text": "Hello"})
        data = response.json()
        assert "entities" in data
        assert isinstance(data["entities"], list)


class TestExtractBatchEndpoint:
    """
    Tests for batch extract endpoint.
    """

    def test_batch_extract_returns_200(self, client: TestClient) -> None:
        """
        Batch extract endpoint should return 200.
        """
        response = client.post(
            "/extract/batch",
            json={"texts": ["Text one", "Text two"]},
        )
        assert response.status_code == 200

    def test_batch_extract_returns_list(self, client: TestClient) -> None:
        """
        Batch extract should return a list of results.
        """
        response = client.post(
            "/extract/batch",
            json={"texts": ["One", "Two", "Three"]},
        )
        data = response.json()
        assert len(data) == 3
