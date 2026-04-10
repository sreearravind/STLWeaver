"""Basic API endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    """The health endpoint should respond with a simple OK payload."""
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["app_name"] == "STLWeaver"
    assert payload["version"] == "0.1.0"


def test_providers_endpoint_returns_placeholder_provider_data() -> None:
    """The providers endpoint should expose the configured placeholder providers."""
    response = client.get("/providers")

    assert response.status_code == 200
    payload = response.json()

    assert "providers" in payload
    assert any(provider["name"] == "openai" for provider in payload["providers"])


def test_generate_endpoint_returns_structured_placeholder_response() -> None:
    """The generate endpoint should return a connected placeholder response."""
    response = client.post(
        "/generate",
        json={
            "prompt": "Create a simple bracket",
            "llm_provider": "openai",
            "analyze_supports": True,
        },
    )

    assert response.status_code == 202
    payload = response.json()

    assert payload["status"] == "accepted"
    assert payload["llm_provider"] == "openai"
    assert payload["code_generated"] is True
    assert payload["security_passed"] is True
    assert payload["supports_analyzed"] is True
    assert payload["support_recommendation"] == "none"
