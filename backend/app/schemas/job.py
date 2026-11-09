from pydantic import BaseModel, Field


class JobInformation(BaseModel):
    company_name: str | None = None
    job_title: str | None = None
    job_type: str | None = None
    location: str | None = None
    salary: str | None = None
    stipend: str | None = None

    recruiter_name: str | None = None
    recruiter_email: str | None = None
    phone: str | None = None

    company_website: str | None = None
    job_url: str | None = None

    payment_requested: bool = False
    payment_amount: str | None = None
    payment_reason: str | None = None

    claims: list[str] = Field(default_factory=list)
