from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.agents.company_verification_agent import (
    CompanyVerificationAgent,
)
from app.agents.job_verification_agent import (
    JobVerificationAgent,
)
from app.agents.report_agent import ReportAgent
from app.agents.risk_agent import RiskAgent
from app.agents.extraction_agent import ExtractionAgent

from app.schemas.evidence import Evidence
from app.tools.document_tools import extract_pdf_text


class AnalysisService:

    def __init__(self):

        # --------------------------------------------------
        # In-memory analysis storage
        # --------------------------------------------------

        self.analyses = {}

        # --------------------------------------------------
        # Agents
        # --------------------------------------------------

        self.extraction = ExtractionAgent()
        self.company = CompanyVerificationAgent()
        self.job = JobVerificationAgent()
        self.risk = RiskAgent()
        self.report = ReportAgent()

        # --------------------------------------------------
        # Upload directory
        # --------------------------------------------------

        self.upload_dir = Path("uploads")

        self.upload_dir.mkdir(
            exist_ok=True
        )

    # ======================================================
    # CREATE ANALYSIS
    # ======================================================

    def create_analysis(
        self,
        text: str,
        source_url: str | None,
    ):

        analysis_id = str(uuid4())

        self.analyses[analysis_id] = {
            "id": analysis_id,
            "status": "PENDING",
            "text": text or "",
            "source_url": source_url,
            "file_paths": [],
            "result": None,
        }

        return {
            "analysis_id": analysis_id,
            "status": "PENDING",
        }

    # ======================================================
    # SAVE UPLOAD
    # ======================================================

    async def save_upload(
        self,
        analysis_id: UUID,
        file: UploadFile,
    ):

        key = str(analysis_id)

        if key not in self.analyses:
            raise KeyError(key)

        # --------------------------------------------------
        # Allowed file types
        # --------------------------------------------------

        allowed = {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".txt",
        }

        suffix = Path(
            file.filename or ""
        ).suffix.lower()

        if suffix not in allowed:
            raise ValueError(
                f"Unsupported file type: "
                f"{suffix or 'unknown'}"
            )

        # --------------------------------------------------
        # Read file
        # --------------------------------------------------

        data = await file.read()

        # 10 MB limit
        if len(data) > 10 * 1024 * 1024:
            raise ValueError(
                "File exceeds the 10 MB MVP limit."
            )

        # --------------------------------------------------
        # Safe filename
        # --------------------------------------------------

        filename = Path(
            file.filename or "upload"
        ).name

        destination = (
            self.upload_dir
            / f"{key}_{filename}"
        )

        destination.write_bytes(data)

        # --------------------------------------------------
        # Save path
        # --------------------------------------------------

        self.analyses[key][
            "file_paths"
        ].append(
            str(destination)
        )

        return {
            "filename": file.filename,
            "stored": True,
        }

    # ======================================================
    # RUN ANALYSIS
    # ======================================================

    def run_analysis(
        self,
        analysis_id: UUID,
    ):

        key = str(analysis_id)

        if key not in self.analyses:
            raise KeyError(key)

        item = self.analyses[key]

        item["status"] = "PROCESSING"

        # ==================================================
        # 1. COLLECT SUBMITTED TEXT
        # ==================================================

        text = item["text"] or ""

        # ==================================================
        # 2. FIND PDF FILES
        # ==================================================

        pdf_paths = [
            path
            for path in item["file_paths"]
            if path.lower().endswith(".pdf")
        ]

        # ==================================================
        # 3. FIND TXT FILES
        # ==================================================

        txt_paths = [
            path
            for path in item["file_paths"]
            if path.lower().endswith(".txt")
        ]

        # ==================================================
        # 4. EXTRACT PDF TEXT
        # ==================================================

        if pdf_paths:

            pdf_text = "\n".join(
                extract_pdf_text(path)
                for path in pdf_paths
            )

            text += "\n" + pdf_text

        # ==================================================
        # 5. EXTRACT TXT TEXT
        # ==================================================

        if txt_paths:

            txt_text = "\n".join(
                Path(path).read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                for path in txt_paths
            )

            text += "\n" + txt_text

        # ==================================================
        # 6. CHECK WHETHER TEXT EXISTS
        # ==================================================

        if not text.strip():

            item["status"] = "FAILED"

            raise ValueError(
                "No readable text was found in "
                "the submitted opportunity."
            )

        # ==================================================
        # 7. EXTRACT JOB INFORMATION
        # ==================================================

        job = self.extraction.extract(
            text,
            item["source_url"],
        )

        # ==================================================
        # 8. COMPANY VERIFICATION
        # ==================================================

        company_result = self.company.verify(
            job.company_name,
            submitted_url=job.company_website,
            location=job.location,
        )

        # --------------------------------------------------
        # Development debug output
        # --------------------------------------------------

        print("\n" + "=" * 80)
        print("JOBSHIELD COMPANY VERIFICATION RESULT")
        print("=" * 80)

        print(
            f"Company: {job.company_name}"
        )

        print(
            f"Submitted location: {job.location}"
        )

        print(
            f"Submitted website: {job.company_website}"
        )

        print("-" * 80)

        print(company_result)

        print("=" * 80 + "\n")

        # ==================================================
        # 9. JOB VERIFICATION
        # ==================================================

        job_result = self.job.verify(
            job.company_name,
            job.job_title,
        )

        # --------------------------------------------------
        # Development debug output
        # --------------------------------------------------

        print("\n" + "=" * 80)
        print("JOBSHIELD JOB VERIFICATION RESULT")
        print("=" * 80)

        print(job_result)

        print("=" * 80 + "\n")

        # ==================================================
        # 10. RISK ANALYSIS
        # ==================================================

        assessment = self.risk.analyze(
            text=text,
            job=job,
            company_result=company_result,
            job_result=job_result,
        )

        # --------------------------------------------------
        # Development debug output
        # --------------------------------------------------

        print("\n" + "=" * 80)
        print("JOBSHIELD RISK ASSESSMENT")
        print("=" * 80)

        print(
            f"Risk score: "
            f"{assessment.get('risk_score')}"
        )

        print(
            f"Risk level: "
            f"{assessment.get('risk_level')}"
        )

        print("Signals:")

        for signal in assessment.get(
            "signals",
            [],
        ):

            print(
                f"- {signal.get('signal_type')}: "
                f"{signal.get('score')} points | "
                f"{signal.get('description')}"
            )

        print("=" * 80 + "\n")

        # ==================================================
        # 11. BUILD EVIDENCE
        # ==================================================

        evidence = []

        # --------------------------------------------------
        # Company
        # --------------------------------------------------

        if job.company_name:

            evidence.append(
                Evidence(
                    evidence_type="EXTRACTED_FACT",
                    source="user_submission",
                    claim="Company name",
                    content=job.company_name,
                    verified=False,
                )
            )

        # --------------------------------------------------
        # Job title
        # --------------------------------------------------

        if job.job_title:

            evidence.append(
                Evidence(
                    evidence_type="EXTRACTED_FACT",
                    source="user_submission",
                    claim="Job title",
                    content=job.job_title,
                    verified=False,
                )
            )

        # --------------------------------------------------
        # Recruiter email
        # --------------------------------------------------

        if job.recruiter_email:

            evidence.append(
                Evidence(
                    evidence_type="EXTRACTED_FACT",
                    source="user_submission",
                    claim="Recruiter email",
                    content=job.recruiter_email,
                    verified=False,
                )
            )

        # --------------------------------------------------
        # Company website
        # --------------------------------------------------

        if job.company_website:

            evidence.append(
                Evidence(
                    evidence_type="SUBMITTED_URL",
                    source="user_submission",
                    claim="Company website",
                    content=job.company_website,
                    url=job.company_website,
                    verified=False,
                )
            )

        # --------------------------------------------------
        # Job / application URL
        # --------------------------------------------------

        if job.job_url:

            evidence.append(
                Evidence(
                    evidence_type="SUBMITTED_URL",
                    source="user_submission",
                    claim="Job/application URL",
                    content=job.job_url,
                    url=job.job_url,
                    verified=False,
                )
            )

        # --------------------------------------------------
        # Payment
        # --------------------------------------------------

        if job.payment_requested:

            payment_content = (
                job.payment_amount
                or job.payment_reason
                or "Payment requested"
            )

            evidence.append(
                Evidence(
                    evidence_type="RISK_SIGNAL",
                    source="user_submission",
                    claim="Payment requested",
                    content=payment_content,
                    verified=False,
                )
            )

        # ==================================================
        # COMPANY RESEARCH EVIDENCE
        # ==================================================

        if company_result:

            # ------------------------------------------------
            # Company status
            # ------------------------------------------------

            company_status = company_result.get(
                "company_status"
            )

            if company_status:

                evidence.append(
                    Evidence(
                        evidence_type="VERIFICATION_RESULT",
                        source="company_research",
                        claim="Company status",
                        content=str(
                            company_status
                        ),
                        verified=True,
                    )
                )

            # ------------------------------------------------
            # Registered address
            # ------------------------------------------------

            registered_address = company_result.get(
                "registered_address"
            )

            if registered_address:

                evidence.append(
                    Evidence(
                        evidence_type="VERIFICATION_RESULT",
                        source="company_research",
                        claim="Independently researched address",
                        content=str(
                            registered_address
                        ),
                        verified=True,
                    )
                )

            # ------------------------------------------------
            # Location match
            # ------------------------------------------------

            location_match = company_result.get(
                "location_match"
            )

            if location_match:

                evidence.append(
                    Evidence(
                        evidence_type="VERIFICATION_RESULT",
                        source="company_research",
                        claim="Location verification",
                        content=str(
                            location_match
                        ),
                        verified=True,
                    )
                )

            # ------------------------------------------------
            # Official website
            # ------------------------------------------------

            official_website = company_result.get(
                "official_website"
            )

            if official_website:

                evidence.append(
                    Evidence(
                        evidence_type="VERIFICATION_RESULT",
                        source="company_research",
                        claim="Official website",
                        content=str(
                            official_website
                        ),
                        url=str(
                            official_website
                        ),
                        verified=True,
                    )
                )

            # ------------------------------------------------
            # Research sources
            # ------------------------------------------------

            sources = company_result.get(
                "sources",
                [],
            )

            if isinstance(
                sources,
                list,
            ):

                for source_item in sources:

                    if not isinstance(
                        source_item,
                        dict,
                    ):
                        continue

                    source_title = (
                        source_item.get(
                            "title"
                        )
                        or "Research source"
                    )

                    source_url = (
                        source_item.get(
                            "url"
                        )
                        or ""
                    )

                    if not source_url:
                        continue

                    evidence.append(
                        Evidence(
                            evidence_type="EXTERNAL_SOURCE",
                            source="company_research",
                            claim=str(
                                source_title
                            ),
                            content=str(
                                source_url
                            ),
                            url=str(
                                source_url
                            ),
                            verified=True,
                        )
                    )

        # ==================================================
        # 12. BUILD REPORT
        # ==================================================

        report = self.report.build(
            key,
            job,
            assessment,
            company_result,
            job_result,
            evidence,
        )

        # ==================================================
        # 13. SAVE RESULT
        # ==================================================

        item["status"] = "COMPLETED"

        item["result"] = report.model_dump()

        return {
            "analysis_id": key,
            "status": "COMPLETED",
            "risk_level": assessment[
                "risk_level"
            ],
            "risk_score": assessment[
                "risk_score"
            ],
        }

    # ======================================================
    # GET ANALYSIS
    # ======================================================

    def get_analysis(
        self,
        analysis_id: UUID,
    ):

        key = str(analysis_id)

        if key not in self.analyses:
            raise KeyError(key)

        item = self.analyses[key]

        return {
            "analysis_id": key,
            "status": item["status"],
            "result": item["result"],
        }

    # ======================================================
    # GET REPORT
    # ======================================================

    def get_report(
        self,
        analysis_id: UUID,
    ):

        key = str(analysis_id)

        if key not in self.analyses:
            raise KeyError(key)

        result = self.analyses[key]["result"]

        if not result:

            raise ValueError(
                "Analysis has not been completed."
            )

        return result