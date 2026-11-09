def verify_job_stub(company_name: str | None, job_title: str | None) -> dict:
    return {
        "status": "NOT_CHECKED",
        "reason": "External job verification provider is not configured in this local MVP.",
        "sources": [],
        "company_name": company_name,
        "job_title": job_title,
    }
