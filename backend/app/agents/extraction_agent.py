from __future__ import annotations

import re

from app.schemas.job import JobInformation


class ExtractionAgent:
    """
    Extract structured job information from submitted text.

    This is a deterministic MVP extractor.
    It does not decide whether the opportunity is fraudulent.
    """

    def run(self, text: str) -> JobInformation:
        text = text or ""

        company_name = self._extract_labeled(
            text,
            [
                "Company Name",
                "Company",
                "Organization",
                "Employer",
            ],
        )

        job_title = self._extract_labeled(
            text,
            [
                "Job Profile",
                "Job Title",
                "Job Role",
                "Position",
                "Role",
            ],
        )

        job_type = self._extract_labeled(
            text,
            [
                "Job Type",
                "Employment Type",
                "Type",
            ],
        )

        location = self._extract_labeled(
            text,
            [
                "Location",
                "Job Location",
                "Work Location",
                "Office Location",
            ],
        )

        salary = self._extract_labeled(
            text,
            [
                "CTC",
                "Salary",
                "Package",
                "Compensation",
            ],
        )

        stipend = self._extract_labeled(
            text,
            [
                "Stipend",
                "Monthly Stipend",
            ],
        )

        recruiter_name = self._extract_labeled(
            text,
            [
                "Recruiter Name",
                "Recruiter",
                "HR Name",
                "Contact Person",
            ],
        )

        recruiter_email = self._extract_email(text)

        phone = self._extract_phone(text)

        company_website = self._extract_company_website(text)

        job_url = self._extract_job_url(text)

        payment_requested = self._detect_payment(text)

        payment_amount = self._extract_payment_amount(text)

        payment_reason = self._extract_payment_reason(text)

        claims = self._extract_claims(text)

        return JobInformation(
            company_name=company_name,
            job_title=job_title,
            job_type=job_type,
            location=location,
            salary=salary,
            stipend=stipend,
            recruiter_name=recruiter_name,
            recruiter_email=recruiter_email,
            phone=phone,
            company_website=company_website,
            job_url=job_url,
            payment_requested=payment_requested,
            payment_amount=payment_amount,
            payment_reason=payment_reason,
            claims=claims,
        )

    # --------------------------------------------------
    # Compatibility method
    # --------------------------------------------------

    def extract(
        self,
        text: str,
        source_url: str | None = None,
    ) -> JobInformation:

        job = self.run(text)

        # If the frontend/API supplied a URL separately,
        # store it as the job URL.
        if source_url:
            job = job.model_copy(
                update={
                    "job_url": source_url
                }
            )

        return job

    # --------------------------------------------------
    # Label extraction
    # --------------------------------------------------

    def _extract_labeled(
        self,
        text: str,
        labels: list[str],
    ) -> str | None:

        for label in labels:

            pattern = (
                rf"(?im)"
                rf"^\s*"
                rf"{re.escape(label)}"
                rf"\s*:\s*"
                rf"(.+?)"
                rf"\s*$"
            )

            match = re.search(
                pattern,
                text,
            )

            if match:
                value = match.group(1).strip()

                if value:
                    return value

        return None

    # --------------------------------------------------
    # Email
    # --------------------------------------------------

    def _extract_email(
        self,
        text: str,
    ) -> str | None:

        match = re.search(
            r"\b[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text,
        )

        return (
            match.group(0)
            if match
            else None
        )

    # --------------------------------------------------
    # Phone
    # --------------------------------------------------

    def _extract_phone(
        self,
        text: str,
    ) -> str | None:

        patterns = [
            r"(?<!\d)\+91[\s-]?[6-9]\d{9}(?!\d)",
            r"(?<!\d)[6-9]\d{9}(?!\d)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
            )

            if match:
                return match.group(0)

        return None

    # --------------------------------------------------
    # URLs
    # --------------------------------------------------

    def _extract_all_urls(
        self,
        text: str,
    ) -> list[str]:

        urls = re.findall(
            r"https?://[^\s<>\"]+",
            text,
        )

        cleaned = []

        for url in urls:

            url = url.rstrip(
                ".,);]}>\"'"
            )

            if url not in cleaned:
                cleaned.append(url)

        return cleaned

    def _extract_company_website(
        self,
        text: str,
    ) -> str | None:

        urls = self._extract_all_urls(text)

        ignored_domains = {
            "forms.gle",
            "docs.google.com",
            "forms.office.com",
            "docs.googleusercontent.com",
            "linkedin.com",
            "www.linkedin.com",
        }

        for url in urls:

            lower_url = url.lower()

            if any(
                domain in lower_url
                for domain in ignored_domains
            ):
                continue

            return url

        return None

    def _extract_job_url(
        self,
        text: str,
    ) -> str | None:

        urls = self._extract_all_urls(text)

        if not urls:
            return None

        # Prefer explicit application/registration URLs.
        for url in urls:

            lower_url = url.lower()

            if any(
                keyword in lower_url
                for keyword in [
                    "apply",
                    "application",
                    "register",
                    "registration",
                    "career",
                    "job",
                ]
            ):
                return url

        # Google Forms is a job/application URL,
        # but not the company's official website.
        for url in urls:

            if "forms.gle" in url.lower():
                return url

        # Otherwise use the first URL.
        return urls[0]

    # --------------------------------------------------
    # Payment detection
    # --------------------------------------------------

    def _detect_payment(
        self,
        text: str,
    ) -> bool:

        patterns = [
            r"registration\s+fee",
            r"application\s+fee",
            r"processing\s+fee",
            r"joining\s+fee",
            r"security\s+deposit",
            r"pay\s+to\s+apply",
            r"payment\s+required",
            r"pay\s+₹",
            r"pay\s+rs\.?",
            r"pay\s+inr",
            r"send\s+money",
            r"transfer\s+money",
        ]

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):
                return True

        return False

    # --------------------------------------------------
    # Payment amount
    # --------------------------------------------------

    def _extract_payment_amount(
        self,
        text: str,
    ) -> str | None:

        patterns = [
            r"(?:registration|application|processing|joining|security)"
            r"\s+(?:fee|deposit)"
            r".{0,40}?"
            r"(₹\s?[\d,]+|Rs\.?\s?[\d,]+|INR\s?[\d,]+)",

            r"pay\s+"
            r"(₹\s?[\d,]+|Rs\.?\s?[\d,]+|INR\s?[\d,]+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return match.group(1)

        return None

    # --------------------------------------------------
    # Payment reason
    # --------------------------------------------------

    def _extract_payment_reason(
        self,
        text: str,
    ) -> str | None:

        labels = [
            "registration fee",
            "application fee",
            "processing fee",
            "joining fee",
            "security deposit",
        ]

        for label in labels:

            if re.search(
                label,
                text,
                re.IGNORECASE,
            ):
                return label

        return None

    # --------------------------------------------------
    # Claims
    # --------------------------------------------------

    def _extract_claims(
        self,
        text: str,
    ) -> list[str]:

        claims = []

        patterns = [
            r"(\d+\s*LPA)",
            r"(\d+\s*Lakh)",
            r"(\d+\s*months?\s*internship)",
            r"(internship\s*\+\s*PPO)",
            r"(work\s+from\s+home)",
            r"(100%\s*remote)",
            r"(guaranteed\s+job)",
            r"(guaranteed\s+placement)",
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE,
            )

            for match in matches:

                value = (
                    match
                    if isinstance(match, str)
                    else match[0]
                )

                value = value.strip()

                if value and value not in claims:
                    claims.append(value)

        return claims