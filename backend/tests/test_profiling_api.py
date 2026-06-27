from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.api.profiling import get_profiling_service
from backend.app.main import app
from backend.app.services.data_intake_service import DataIntakeService
from backend.app.services.profiling_service import ProfilingService


def test_create_profile_endpoint(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    intake_service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )
    metadata = intake_service.inspect_file(generated_sample_paths["csv"])
    profiling_service = ProfilingService(
        intake_service=intake_service,
        reports_dir=tmp_path / "reports" / "profiles",
    )
    app.dependency_overrides[get_profiling_service] = lambda: profiling_service
    client = TestClient(app)

    response = client.post(f"/api/profiling/assets/{metadata.asset_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_id"] == metadata.asset_id
    assert payload["file_name"] == "customers.csv"
    assert payload["quality_summary"]["columns_with_missing_values"]


def test_list_profile_reports_endpoint(
    tmp_path: Path,
    generated_sample_paths: dict[str, Path],
) -> None:
    intake_service = DataIntakeService(
        raw_data_dir=tmp_path / "raw",
        metadata_path=tmp_path / "raw" / ".metadata.json",
    )
    profiling_service = ProfilingService(
        intake_service=intake_service,
        reports_dir=tmp_path / "reports" / "profiles",
    )
    profile = profiling_service.profile_file(generated_sample_paths["parquet"])
    app.dependency_overrides[get_profiling_service] = lambda: profiling_service
    client = TestClient(app)

    response = client.get("/api/profiling/reports")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["profile_id"] == profile.profile_id
