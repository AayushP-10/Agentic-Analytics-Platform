from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.api.intake import get_intake_service
from backend.app.main import app
from backend.app.services.data_intake_service import DataIntakeService


def test_upload_endpoint_accepts_csv(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )
    app.dependency_overrides[get_intake_service] = lambda: service
    client = TestClient(app)

    with generated_sample_paths["csv"].open("rb") as file:
        response = client.post(
            "/api/intake/upload",
            files={"file": ("customers.csv", file, "text/csv")},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_name"] == "customers.csv"
    assert payload["format"] == "csv"
    assert payload["row_count"] == 7
    assert "customer_id" in payload["columns"]


def test_assets_endpoint_lists_persisted_upload(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )
    metadata = service.inspect_file(generated_sample_paths["csv"])
    app.dependency_overrides[get_intake_service] = lambda: service
    client = TestClient(app)

    response = client.get("/api/intake/assets")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["asset_id"] == metadata.asset_id
