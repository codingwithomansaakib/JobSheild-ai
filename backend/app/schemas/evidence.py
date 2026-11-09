from pydantic import BaseModel


class Evidence(BaseModel):
    evidence_type: str
    source: str
    claim: str
    content: str
    url: str | None = None
    confidence: float = 1.0
    verified: bool = False
