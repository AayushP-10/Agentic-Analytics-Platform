from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from backend.app.schemas.intake import DataAssetMetadata
from backend.app.services.data_intake_service import (
    DataIntakeService,
    IntakeFileError,
    UnsupportedFileTypeError,
)
from backend.app.services.readers.base import DataReaderError

router = APIRouter(prefix="/api/intake", tags=["intake"])


def get_intake_service() -> DataIntakeService:
    return DataIntakeService()


@router.post("/upload", response_model=DataAssetMetadata)
def upload_asset(
    file: Annotated[UploadFile, File()],
    service: Annotated[DataIntakeService, Depends(get_intake_service)],
) -> DataAssetMetadata:
    try:
        saved_path = service.save_upload(file.filename or "", file.file)
        return service.inspect_file(saved_path)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IntakeFileError as exc:
        status_code = (
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            if "maximum upload size" in str(exc)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except DataReaderError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/assets")
def list_assets(
    service: Annotated[DataIntakeService, Depends(get_intake_service)],
) -> list[dict[str, object]]:
    return service.list_assets()


@router.get("/assets/{asset_id}", response_model=DataAssetMetadata)
def get_asset(
    asset_id: str,
    service: Annotated[DataIntakeService, Depends(get_intake_service)],
) -> DataAssetMetadata:
    try:
        return service.get_asset(asset_id)
    except IntakeFileError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
