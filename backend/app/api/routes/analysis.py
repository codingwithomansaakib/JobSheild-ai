from uuid import UUID

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.services.analysis_service import AnalysisService


router = APIRouter(
    prefix="/analyses",
    tags=["Analyses"],
)


# IMPORTANT:
# Create ONE service instance.
# Do NOT create AnalysisService() inside every endpoint.
analysis_service = AnalysisService()


class CreateAnalysisRequest(BaseModel):
    text: str = ""
    source_url: str | None = None


@router.post("")
def create_analysis(
    payload: CreateAnalysisRequest,
):
    return analysis_service.create_analysis(
        text=payload.text,
        source_url=payload.source_url,
    )


@router.post("/{analysis_id}/files")
async def upload_file(
    analysis_id: UUID,
    file: UploadFile = File(...),
):
    return await analysis_service.save_upload(
        analysis_id=analysis_id,
        file=file,
    )


@router.post("/{analysis_id}/run")
def run_analysis(
    analysis_id: UUID,
):
    return analysis_service.run_analysis(
        analysis_id=analysis_id,
    )


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: UUID,
):
    return analysis_service.get_analysis(
        analysis_id=analysis_id,
    )


@router.get("/{analysis_id}/report")
def get_report(
    analysis_id: UUID,
):
    return analysis_service.get_report(
        analysis_id=analysis_id,
    )