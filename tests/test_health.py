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
    assert payload["stage"] == "ready"
    assert payload["mode"] == "placeholder_scaffold"
    assert payload["app_name"] == "STLWeaver"
    assert payload["version"] == "0.1.0"


def test_providers_endpoint_returns_placeholder_provider_data() -> None:
    """The providers endpoint should expose the configured placeholder providers."""
    response = client.get("/providers")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["stage"] == "inspection"
    assert "providers" in payload
    assert any(provider["name"] == "openai" for provider in payload["providers"])


def test_info_endpoint_returns_local_inspection_metadata() -> None:
    """The info endpoint should expose local inspection metadata."""
    response = client.get("/info")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["stage"] == "inspection"
    assert payload["mode"] == "placeholder_scaffold"
    assert "/preview" in payload["available_endpoints"]
    assert "openai" in payload["supported_providers"]


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
    assert payload["stage"] == "queued"
    assert payload["llm_provider"] == "openai"
    assert payload["created_at"]
    assert payload["prompt_summary"]["text"] == "Create a simple bracket"
    assert payload["code_generated"] is True
    assert payload["security_passed"] is True
    assert payload["supports_analyzed"] is True
    assert payload["support_recommendation"] == "none"


def test_status_endpoint_returns_placeholder_job_state() -> None:
    """The status endpoint should return the stored placeholder job state."""
    create_response = client.post(
        "/generate",
        json={
            "prompt": "Create a simple bracket",
            "llm_provider": "openai",
            "analyze_supports": False,
        },
    )
    job_id = create_response.json()["job_id"]

    response = client.get(f"/status/{job_id}")

    assert response.status_code == 200
    payload = response.json()

    assert payload["job_id"] == job_id
    assert payload["status"] == "pending"
    assert payload["stage"] == "validated"
    assert payload["llm_provider"] == "openai"
    assert payload["created_at"]
    assert payload["prompt_summary"]["text"] == "Create a simple bracket"
    assert payload["supports_analyzed"] is False


def test_status_endpoint_returns_404_for_unknown_job() -> None:
    """The status endpoint should reject unknown job identifiers cleanly."""
    response = client.get("/status/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "No placeholder job found for job_id 'does-not-exist'."


def test_generate_endpoint_rejects_unsupported_provider() -> None:
    """The generate endpoint should reject unsupported providers."""
    response = client.post(
        "/generate",
        json={
            "prompt": "Create a simple bracket",
            "llm_provider": "not-a-provider",
            "analyze_supports": True,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]

    assert "Unsupported provider 'not-a-provider'." in detail
    assert "Supported providers:" in detail


def test_generate_endpoint_rejects_empty_prompt() -> None:
    """The generate endpoint should reject whitespace-only prompts."""
    response = client.post(
        "/generate",
        json={
            "prompt": "   ",
            "llm_provider": "openai",
            "analyze_supports": True,
        },
    )

    assert response.status_code == 422
    detail = response.json()["detail"]

    assert any("Prompt must not be empty." in entry["msg"] for entry in detail)


def test_preview_endpoint_returns_structured_placeholder_preview() -> None:
    """The preview endpoint should expose simulated preview metadata."""
    response = client.post(
        "/preview",
        json={
            "prompt": "Create a compact phone stand with a cable slot",
            "llm_provider": "openai",
            "analyze_supports": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["stage"] == "preview_ready"
    assert payload["llm_provider"] == "openai"
    assert payload["prompt_summary"]["length"] > 0
    assert payload["code_preview"]["generated"] is True
    assert payload["geometry_preview"]["available"] is False
    assert payload["support_preview"]["analyzed"] is True
    assert payload["support_preview"]["recommended_type"] == "none"
