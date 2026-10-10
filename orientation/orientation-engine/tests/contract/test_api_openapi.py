from fastapi.testclient import TestClient

from orientation.main import app

client = TestClient(app)


def test_openapi_exposes_core_paths() -> None:
    spec = client.get("/openapi.json").json()
    assert spec["info"]["title"]
    assert "/v1/orientation/recommendations" in spec["paths"]
    assert "/v1/orientation/system/info" in spec["paths"]


def test_health_endpoint() -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_system_info_returns_versions() -> None:
    data = client.get("/v1/orientation/system/info").json()
    assert data["code_version"]
    assert data["model_version"]
    assert "database" in data


def test_recommendation_rejects_empty_payload() -> None:
    response = client.post("/v1/orientation/recommendations", json={})
    assert response.status_code == 422


def test_pages_render_without_placeholder() -> None:
    for path in ("/", "/moteur", "/principes", "/etat", "/developers"):
        body = client.get(path).text
        assert "{{include:" not in body
        assert '<nav id="nav">' in body
        assert "<footer>" in body
