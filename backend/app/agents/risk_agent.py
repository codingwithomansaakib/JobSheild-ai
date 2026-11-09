from __future__ import annotations

from app.tools.risk_tools import assess_risk


class RiskAgent:
    """
    Coordinates the deterministic JobShield risk engine.

    The risk engine combines:
    - submitted message signals
    - company verification signals
    - job verification signals

    It returns an evidence-based risk assessment.
    """

    def analyze(
        self,
        text: str,
        job,
        company_result: dict | None = None,
        job_result: dict | None = None,
    ) -> dict:

        return assess_risk(
            text=text,
            job=job,
            company_result=company_result,
            job_result=job_result,
        )