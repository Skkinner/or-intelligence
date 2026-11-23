"""API tests for WBS 4.2.1 / 4.2.2 (Member C), using FastAPI TestClient in fixture mode."""

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from src.api.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_every_contract_path_is_routed():
    """Every path in contracts/openapi.yaml must exist in the app (stubs return 501 until implemented)."""
    import yaml

    from src.common.contracts import CONTRACTS_DIR

    spec = yaml.safe_load((CONTRACTS_DIR / "openapi.yaml").read_text(encoding="utf-8"))
    routed = {p.replace("{video_id}", "{id}") for p in app.openapi()["paths"]}
    missing = [p for p in spec["paths"] if p not in routed]
    assert not missing, f"paths in openapi.yaml without a route: {missing}"


@pytest.mark.skip(reason="TODO WBS 4.2.1 (Member C): upload -> done -> timeline in fixture mode")
def test_upload_reaches_done_in_fixture_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("INFERENCE_MODE", "fixture")
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    r = client.post("/api/videos", files={"file": ("x.mp4", b"\x00" * 10, "video/mp4")})
    assert r.status_code == 202


@pytest.mark.skip(reason="TODO WBS 4.2.2 (Member C): search returns exactly the clipper segments")
def test_search_clipper_on_fixture():
    from src.api.routes.search import search_timelines

    assert search_timelines([], "clipper") == []
