from pydantic import BaseModel


class RiskSignal(BaseModel):
    signal_type: str
    severity: str
    weight: int
    detected: bool
    description: str
    evidence: str | None = None


class RiskAssessment(BaseModel):
    risk_level: str
    risk_score: int
    signals: list[RiskSignal]
