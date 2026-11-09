from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence
from app.schemas.job import JobInformation
from app.schemas.risk import RiskAssessment


class AnalysisReport(BaseModel):
    analysis_id: str
    job: JobInformation
    assessment: RiskAssessment
    verified_facts: list[str] = Field(default_factory=list)
    unverified_items: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    summary: str
