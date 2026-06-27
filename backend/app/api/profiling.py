from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.schemas.profiling import DatasetProfile
from backend.app.services.profiling_service import ProfilingError, ProfilingService

router = APIRouter(prefix="/api/profiling", tags=["profiling"])


def get_profiling_service() -> ProfilingService:
    return ProfilingService()


@router.post("/assets/{asset_id}", response_model=DatasetProfile)
def create_profile(
    asset_id: str,
    service: Annotated[ProfilingService, Depends(get_profiling_service)],
    table_name: Annotated[str | None, Query()] = None,
) -> DatasetProfile:
    try:
        return service.profile_asset(asset_id, table_name=table_name)
    except ProfilingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/reports")
def list_profile_reports(
    service: Annotated[ProfilingService, Depends(get_profiling_service)],
) -> list[dict[str, object]]:
    return service.list_reports()


@router.get("/reports/{profile_id}", response_model=DatasetProfile)
def get_profile_report(
    profile_id: str,
    service: Annotated[ProfilingService, Depends(get_profiling_service)],
) -> DatasetProfile:
    try:
        return service.get_report(profile_id)
    except ProfilingError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
