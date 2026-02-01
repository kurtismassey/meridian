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


class TestRecogniseEndpoint:
    """
    Tests for recognise endpoint.
    """

    def test_recognise_returns_200(self, client: TestClient) -> None:
        """
        Recognise endpoint should return 200 for valid request.
        """
        response = client.post("/recognise", json={"text": "Hey Meridian"})
        assert response.status_code == 200

    def test_recognise_returns_text(self, client: TestClient) -> None:
        """
        Recognise endpoint should return the original text.
        """
        response = client.post("/recognise", json={"text": "Test input"})
        data = response.json()
        assert data["text"] == "Test input"

    def test_recognise_returns_entities_list(self, client: TestClient) -> None:
        """
        Recognise endpoint should return entities list.
        """
        response = client.post("/recognise", json={"text": "Hello"})
        data = response.json()
        assert "entities" in data
        assert isinstance(data["entities"], list)


class TestRecogniseBatchEndpoint:
    """
    Tests for batch recognise endpoint.
    """

    def test_recognise_batch_returns_200(self, client: TestClient) -> None:
        """
        Batch recognise endpoint should return 200.
        """
        response = client.post(
            "/recognise/batch",
            json={"texts": ["Text one", "Text two"]},
        )
        assert response.status_code == 200

    def test_recognise_batch_returns_list(self, client: TestClient) -> None:
        """
        Batch recognise should return a list of results.
        """
        response = client.post(
            "/recognise/batch",
            json={"texts": ["One", "Two", "Three"]},
        )
        data = response.json()
        assert len(data) == 3
