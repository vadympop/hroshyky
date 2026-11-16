from pathlib import Path

from fastapi.testclient import TestClient

from hroshyky.api.app import create_app
from hroshyky.tools import export_openapi

COMMITTED_SCHEMA = Path(__file__).resolve().parents[1] / "openapi.json"


def test_health_answers_ok() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_committed_openapi_schema_matches_the_code() -> None:
    assert COMMITTED_SCHEMA.read_text(encoding="utf-8") == export_openapi.render()


def test_export_writes_the_schema(tmp_path: Path) -> None:
    target = tmp_path / "schema.json"

    assert export_openapi.main([str(target)]) == 0
    assert target.read_text(encoding="utf-8") == export_openapi.render()


def test_export_without_a_path_shows_usage() -> None:
    assert export_openapi.main([]) == 2
