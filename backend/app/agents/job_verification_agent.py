from app.tools.job_tools import verify_job_stub


class JobVerificationAgent:
    def verify(self, company_name: str | None, job_title: str | None) -> dict:
        return verify_job_stub(company_name, job_title)
