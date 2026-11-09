from __future__ import annotations

from app.schemas.report import AnalysisReport


class ReportAgent:
    def build(
        self,
        analysis_id: str,
        job,
        assessment: dict,
        company_result: dict,
        job_result: dict,
        evidence: list,
    ) -> AnalysisReport:

        # -------------------------------------------------
        # 1. Collect detected risk warnings
        # -------------------------------------------------
        warnings = [
            signal["description"]
            for signal in assessment.get("signals", [])
            if signal.get("detected")
        ]

        # -------------------------------------------------
        # 2. Verified facts
        # -------------------------------------------------
        verified_facts = []

        if company_result.get("status") == "VERIFIED":
            verified_facts.append(
                "Company information was verified by a configured verification source."
            )

        if job_result.get("status") == "MATCH":
            verified_facts.append(
                "The job opportunity matched a configured verification source."
            )

        # -------------------------------------------------
        # 3. Research / verification status
        # -------------------------------------------------
        if company_result.get("status") == "RESEARCHED":
            research = company_result.get("research", "")

            if research:
                verified_facts.append(
                    "Company research was performed using an external research provider."
                )

        # -------------------------------------------------
        # 4. Items that remain unverified
        # -------------------------------------------------
        unverified = []

        company_status = company_result.get("status")

        if company_status not in {"VERIFIED", "RESEARCHED"}:
            unverified.append(
                "Company identity could not be independently verified."
            )

        if company_status == "RESEARCHED":
            unverified.append(
                "Company research was performed, but research results do not by themselves prove that the submitted job offer is legitimate."
            )

        if job_result.get("status") != "MATCH":
            unverified.append(
                "The specific job opportunity could not be independently verified."
            )

        # -------------------------------------------------
        # 5. Recommendations
        # -------------------------------------------------
        recommendations = [
            "Verify the opportunity through the company's official website or careers page.",
            "Do not send money or sensitive personal information solely because a recruiter requests it.",
        ]

        # Add risk-specific recommendations
        signal_types = {
            signal.get("type")
            for signal in assessment.get("signals", [])
            if signal.get("detected")
        }

        if "PAYMENT_REQUEST" in signal_types:
            recommendations.insert(
                0,
                "Do not pay any registration, interview, training, security, or account-opening fee.",
            )

        if "COMPANY_STATUS_CONFLICT" in signal_types:
            recommendations.insert(
                0,
                "Verify the legal status and identity of the company using official corporate records.",
            )

        if "COMPANY_ADDRESS_MISMATCH" in signal_types:
            recommendations.insert(
                0,
                "Verify that the address in the message belongs to the same legal entity as the company being advertised.",
            )

        if "PUBLIC_COMPLAINTS" in signal_types:
            recommendations.insert(
                0,
                "Review the cited complaint evidence carefully and confirm whether it refers to the same company and opportunity.",
            )

        if "SUSPICIOUS_URL" in signal_types:
            recommendations.insert(
                0,
                "Verify the application link before submitting personal information.",
            )

        # -------------------------------------------------
        # 6. Summary
        # -------------------------------------------------
        risk_level = assessment.get(
            "risk_level",
            "UNABLE_TO_VERIFY",
        )

        risk_score = assessment.get(
            "risk_score",
            0,
        )

        warning_count = len(warnings)

        if risk_level == "HIGH":
            summary = (
                f"JobShield identified {warning_count} warning signal(s) "
                f"with a heuristic risk score of {risk_score}/100. "
                "The assessment indicates significant warning indicators "
                "that require verification before proceeding. "
                "This is an evidence-based risk assessment, not a definitive "
                "fraud determination."
            )

        elif risk_level == "MEDIUM":
            summary = (
                f"JobShield identified {warning_count} warning signal(s) "
                f"with a heuristic risk score of {risk_score}/100. "
                "Some aspects of the opportunity require additional verification "
                "before proceeding. "
                "This is an evidence-based risk assessment, not a definitive "
                "fraud determination."
            )

        elif risk_level == "LOW":
            summary = (
                f"JobShield identified {warning_count} warning signal(s) "
                f"with a heuristic risk score of {risk_score}/100. "
                "No major warning indicators were detected from the currently "
                "available evidence. "
                "This does not guarantee that the opportunity is legitimate."
            )

        else:
            summary = (
                "JobShield could not establish enough evidence to calculate "
                "a meaningful risk assessment. Additional verification is required."
            )

        # -------------------------------------------------
        # 7. Build final report
        # -------------------------------------------------
        return AnalysisReport(
            analysis_id=analysis_id,
            job=job,
            assessment=assessment,
            verified_facts=verified_facts,
            unverified_items=unverified,
            recommendations=recommendations,
            evidence=evidence,
            summary=summary,
        )