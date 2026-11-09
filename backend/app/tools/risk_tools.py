from __future__ import annotations

import re
from typing import Any


# ============================================================
# RISK WEIGHTS
# ============================================================

RISK_WEIGHTS = {
    "PAYMENT_REQUEST": 30,
    "SENSITIVE_INFORMATION": 25,
    "SUSPICIOUS_URL": 20,
    "EMAIL_DOMAIN_MISMATCH": 15,

    "COMPANY_STATUS_CONFLICT": 30,
    "COMPANY_ADDRESS_MISMATCH": 20,
    "COMPANY_LOCATION_NOT_VERIFIED": 5,
    "PUBLIC_COMPLAINTS": 20,

    "JOB_NOT_VERIFIED": 15,
    "RECRUITER_NOT_VERIFIED": 10,

    "URGENCY": 10,
    "WORK_FROM_HOME_CLAIM": 5,
    "INCONSISTENCY": 10,
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def contains_any(
    text: str,
    keywords: list[str],
) -> bool:

    text = normalize_text(text)

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


def make_signal(
    signal_type: str,
    severity: str,
    description: str,
    evidence: str,
    score: int,
) -> dict:

    return {
        "signal_type": signal_type,
        "severity": severity,
        "description": description,
        "evidence": evidence,
        "score": int(score),
        "weight": int(score),
        "detected": True,
    }


def get_research_text(
    company_result: dict | None,
) -> str:

    if not company_result:
        return ""

    research = company_result.get("research")

    if isinstance(research, str):
        return research

    if research is None:
        return ""

    return str(research)


# ============================================================
# MESSAGE SIGNALS
# ============================================================

def detect_message_signals(
    text: str,
    job: Any,
) -> list[dict]:

    text = text or ""
    text_lower = normalize_text(text)

    signals: list[dict] = []

    # --------------------------------------------------------
    # PAYMENT REQUEST
    # --------------------------------------------------------

    payment_patterns = [
        r"\bpay\b",
        r"\bpayment\b",
        r"\bregistration fee\b",
        r"\bprocessing fee\b",
        r"\bsecurity fee\b",
        r"\baccount opening fee\b",
        r"\bjob fee\b",
        r"\bjoining fee\b",
        r"\bplacement fee\b",
        r"\btraining fee\b",
        r"\bdeposit\b",
        r"₹\s?\d+",
        r"\brs\.?\s?\d+",
        r"\binr\s?\d+",
    ]

    payment_detected = any(
        re.search(
            pattern,
            text_lower,
        )
        for pattern in payment_patterns
    )

    if payment_detected:

        signals.append(
            make_signal(
                signal_type="PAYMENT_REQUEST",
                severity="HIGH",
                description=(
                    "The submitted opportunity contains "
                    "language that may indicate a payment "
                    "or fee request."
                ),
                evidence=(
                    "Payment-related language was detected "
                    "in the submitted message."
                ),
                score=RISK_WEIGHTS[
                    "PAYMENT_REQUEST"
                ],
            )
        )

    # --------------------------------------------------------
    # SENSITIVE INFORMATION
    # --------------------------------------------------------

    sensitive_keywords = [
        "otp",
        "password",
        "bank account",
        "banking details",
        "bank details",
        "account number",
        "card number",
        "credit card",
        "debit card",
        "cvv",
        "upi pin",
        "upi password",
        "aadhaar",
        "aadhar",
        "pan card",
        "pan number",
    ]

    if contains_any(
        text_lower,
        sensitive_keywords,
    ):

        signals.append(
            make_signal(
                signal_type="SENSITIVE_INFORMATION",
                severity="HIGH",
                description=(
                    "The message requests or references "
                    "sensitive personal or financial "
                    "information."
                ),
                evidence=(
                    "Sensitive-information keywords were "
                    "detected in the submitted message."
                ),
                score=RISK_WEIGHTS[
                    "SENSITIVE_INFORMATION"
                ],
            )
        )

    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    urgency_keywords = [
        "immediately",
        "urgent",
        "act now",
        "limited time",
        "today only",
        "be on time",
        "confirm immediately",
        "last chance",
        "respond immediately",
        "join immediately",
    ]

    if contains_any(
        text_lower,
        urgency_keywords,
    ):

        signals.append(
            make_signal(
                signal_type="URGENCY",
                severity="MEDIUM",
                description=(
                    "The message uses time-sensitive "
                    "language that may pressure the candidate."
                ),
                evidence=(
                    "Urgency-related wording was detected "
                    "in the submitted message."
                ),
                score=RISK_WEIGHTS["URGENCY"],
            )
        )

    # --------------------------------------------------------
    # WORK FROM HOME
    # --------------------------------------------------------

    work_from_home_keywords = [
        "work from home",
        "work-from-home",
        "wfh",
        "home based",
        "home-based",
        "work remotely",
        "remote work",
    ]

    if contains_any(
        text_lower,
        work_from_home_keywords,
    ):

        signals.append(
            make_signal(
                signal_type="WORK_FROM_HOME_CLAIM",
                severity="LOW",
                description=(
                    "The opportunity includes a work-from-home "
                    "claim that should be independently verified."
                ),
                evidence=(
                    "Work-from-home language was detected "
                    "in the submitted message."
                ),
                score=RISK_WEIGHTS[
                    "WORK_FROM_HOME_CLAIM"
                ],
            )
        )

    # --------------------------------------------------------
    # URL / DOMAIN
    # --------------------------------------------------------

    suspicious_url_patterns = [
        r"bit\.ly",
        r"tinyurl\.com",
        r"t\.co/",
        r"goo\.gl",
        r"cutt\.ly",
        r"rb\.gy",
        r"shorturl",
        r"forms\.gle",
        r"docs\.google\.com/forms",
    ]

    suspicious_url_detected = any(
        re.search(
            pattern,
            text_lower,
        )
        for pattern in suspicious_url_patterns
    )

    if suspicious_url_detected:

        signals.append(
            make_signal(
                signal_type="SUSPICIOUS_URL",
                severity="MEDIUM",
                description=(
                    "The opportunity uses a third-party or "
                    "shortened application URL that should "
                    "be independently verified."
                ),
                evidence=(
                    "A third-party or shortened URL pattern "
                    "was detected in the submitted content."
                ),
                score=RISK_WEIGHTS[
                    "SUSPICIOUS_URL"
                ],
            )
        )

    # --------------------------------------------------------
    # RECRUITER EMAIL
    # --------------------------------------------------------

    email_match = re.search(
        r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}",
        text,
    )

    if email_match:

        email = email_match.group(0).lower()
        domain = email.split("@")[-1]

        generic_domains = {
            "gmail.com",
            "yahoo.com",
            "hotmail.com",
            "outlook.com",
            "rediffmail.com",
            "protonmail.com",
            "icloud.com",
        }

        company_name = normalize_text(
            getattr(
                job,
                "company_name",
                "",
            )
        )

        company_words = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                company_name,
            )
            if len(word) > 2
        }

        if domain in generic_domains:

            signals.append(
                make_signal(
                    signal_type="EMAIL_DOMAIN_MISMATCH",
                    severity="MEDIUM",
                    description=(
                        "The recruiter email uses a generic "
                        "email provider instead of an identifiable "
                        "company domain."
                    ),
                    evidence=(
                        f"Recruiter email domain: {domain}"
                    ),
                    score=RISK_WEIGHTS[
                        "EMAIL_DOMAIN_MISMATCH"
                    ],
                )
            )

        elif company_words:

            domain_without_tld = re.sub(
                r"\.(com|in|org|net|co|io)$",
                "",
                domain,
            )

            if not any(
                word in domain_without_tld
                for word in company_words
            ):

                signals.append(
                    make_signal(
                        signal_type="EMAIL_DOMAIN_MISMATCH",
                        severity="MEDIUM",
                        description=(
                            "The recruiter email domain does not "
                            "clearly match the submitted company name."
                        ),
                        evidence=(
                            f"Company: {company_name}. "
                            f"Email domain: {domain}."
                        ),
                        score=RISK_WEIGHTS[
                            "EMAIL_DOMAIN_MISMATCH"
                        ],
                    )
                )

    return signals


# ============================================================
# COMPANY HELPERS
# ============================================================

def _extract_registered_address(
    research_text: str,
) -> str:

    if not research_text:
        return ""

    patterns = [
        r"registered address\s*[:\-]\s*(.+?)(?:\n|$)",
        r"registered office\s*[:\-]\s*(.+?)(?:\n|$)",
        r"registered address is\s+(.+?)(?:\n|$)",
        r"registered office is\s+(.+?)(?:\n|$)",
        r"address\s*[:\-]\s*(.+?)(?:\n|$)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            research_text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return ""


def _extract_company_status(
    company_result: dict,
    research_text: str,
) -> str:
    """
    Extract the actual company/legal status.

    IMPORTANT:
    `RESEARCHED` is the research-process status and must
    never be treated as the company's legal status.
    """

    # --------------------------------------------------------
    # Structured status FIRST
    # --------------------------------------------------------

    structured_statuses = [
        company_result.get("company_status"),
        company_result.get("registration_status"),
    ]

    ignored_statuses = {
        "researched",
        "research",
        "found",
        "partially_found",
        "not_found",
        "unable_to_verify",
        "error",
    }

    for status in structured_statuses:

        if status:

            normalized = normalize_text(status)

            if normalized not in ignored_statuses:
                return normalized

    # --------------------------------------------------------
    # Search research text
    # --------------------------------------------------------

    status_patterns = [
        r"status\s*[:\-]\s*(strike off|struck off|active|inactive|dormant|cancelled|canceled|liquidation)",
        r"company status\s*[:\-]\s*(strike off|struck off|active|inactive|dormant|cancelled|canceled|liquidation)",
        r"registration status\s*[:\-]\s*(strike off|struck off|active|inactive|dormant|cancelled|canceled|liquidation)",
        r"\b(strike off)\b",
        r"\b(struck off)\b",
        r"\b(inactive)\b",
        r"\b(dormant)\b",
        r"\b(cancelled)\b",
        r"\b(canceled)\b",
        r"\b(liquidation)\b",
    ]

    for pattern in status_patterns:

        match = re.search(
            pattern,
            research_text,
            re.IGNORECASE,
        )

        if match:

            return normalize_text(
                match.group(1)
            )

    return ""


def _has_strong_complaint_evidence(
    research_text: str,
) -> bool:

    text = normalize_text(
        research_text
    )

    strong_patterns = [
        "job fraud",
        "job scam",
        "fake job",
        "fake jobs",
        "fraud complaint",
        "employment fraud",
        "recruitment fraud",
        "job fraud report",
        "complaint about job",
        "complaint regarding job",
        "asked for money",
        "payment for job",
    ]

    return any(
        pattern in text
        for pattern in strong_patterns
    )


def _has_structured_complaints(
    company_result: dict,
) -> bool:

    complaints = company_result.get(
        "complaints"
    )

    return (
        isinstance(complaints, list)
        and len(complaints) > 0
    )


# ============================================================
# COMPANY VERIFICATION SIGNALS
# ============================================================

def detect_company_signals(
    company_result: dict | None = None,
    submitted_location: str | None = None,
) -> list[dict]:

    signals: list[dict] = []

    if not company_result:
        return signals

    research_text = get_research_text(
        company_result
    )

    company_status = _extract_company_status(
        company_result,
        research_text,
    )

    # --------------------------------------------------------
    # COMPANY STATUS
    # --------------------------------------------------------

    conflict_statuses = {
        "strike off",
        "struck off",
        "inactive",
        "dormant",
        "cancelled",
        "canceled",
        "liquidation",
    }

    if company_status in conflict_statuses:

        signals.append(
            make_signal(
                signal_type="COMPANY_STATUS_CONFLICT",
                severity="HIGH",
                description=(
                    "The independently researched company "
                    "record shows a status that conflicts "
                    "with treating the company as an active employer."
                ),
                evidence=(
                    "Research indicates company status: "
                    f"{company_status}."
                ),
                score=RISK_WEIGHTS[
                    "COMPANY_STATUS_CONFLICT"
                ],
            )
        )

    # --------------------------------------------------------
    # REGISTERED ADDRESS / LOCATION
    # --------------------------------------------------------

    registered_address = (
        company_result.get(
            "registered_address"
        )
        or _extract_registered_address(
            research_text
        )
    )

    submitted_location = str(
        submitted_location or ""
    ).strip()

    location_match = normalize_text(
        company_result.get(
            "location_match"
        )
    )

    # --------------------------------------------------------
    # EXPLICIT MISMATCH FROM RESEARCH
    # --------------------------------------------------------

    if (
        submitted_location
        and location_match == "mismatch"
    ):

        signals.append(
            make_signal(
                signal_type="COMPANY_ADDRESS_MISMATCH",
                severity="MEDIUM",
                description=(
                    "The submitted company location conflicts "
                    "with the independently researched company "
                    "location."
                ),
                evidence=(
                    f"Submitted location: "
                    f"{submitted_location}. "
                    f"Independently researched address: "
                    f"{registered_address or 'Not available'}."
                ),
                score=RISK_WEIGHTS[
                    "COMPANY_ADDRESS_MISMATCH"
                ],
            )
        )

    # --------------------------------------------------------
    # EXPLICIT LOCATION UNKNOWN
    #
    # This is a small verification warning, not evidence
    # that the company is fraudulent.
    # --------------------------------------------------------

    elif (
        submitted_location
        and location_match in {
            "",
            "unknown",
        }
        and not registered_address
    ):

        signals.append(
            make_signal(
                signal_type="COMPANY_LOCATION_NOT_VERIFIED",
                severity="LOW",
                description=(
                    "The submitted company location could not "
                    "be independently verified from the "
                    "available company research."
                ),
                evidence=(
                    f"Submitted location: "
                    f"{submitted_location}. "
                    "No independently confirmed company "
                    "address was returned."
                ),
                score=RISK_WEIGHTS[
                    "COMPANY_LOCATION_NOT_VERIFIED"
                ],
            )
        )

    # --------------------------------------------------------
    # ADDRESS COMPARISON FALLBACK
    # --------------------------------------------------------

    elif (
        submitted_location
        and registered_address
        and location_match not in {
            "match",
            "partial",
        }
    ):

        ignored_words = {
            "india",
            "delhi",
            "new",
            "office",
            "road",
            "near",
            "district",
            "center",
            "centre",
            "metro",
            "station",
            "building",
            "floor",
            "the",
            "and",
            "pvt",
            "private",
            "limited",
            "ltd",
        }

        submitted_terms = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                normalize_text(
                    submitted_location
                ),
            )
            if len(word) > 3
            and word not in ignored_words
        }

        registered_terms = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                normalize_text(
                    registered_address
                ),
            )
            if len(word) > 3
            and word not in ignored_words
        }

        matching_terms = (
            submitted_terms.intersection(
                registered_terms
            )
        )

        if (
            submitted_terms
            and registered_terms
            and not matching_terms
        ):

            signals.append(
                make_signal(
                    signal_type="COMPANY_ADDRESS_MISMATCH",
                    severity="MEDIUM",
                    description=(
                        "The submitted company location does "
                        "not closely match the independently "
                        "found company address."
                    ),
                    evidence=(
                        f"Submitted location: "
                        f"{submitted_location}. "
                        f"Independently found address: "
                        f"{registered_address}."
                    ),
                    score=RISK_WEIGHTS[
                        "COMPANY_ADDRESS_MISMATCH"
                    ],
                )
            )

    # --------------------------------------------------------
    # PUBLIC COMPLAINTS
    # --------------------------------------------------------

    if (
        _has_structured_complaints(
            company_result
        )
        or _has_strong_complaint_evidence(
            research_text
        )
    ):

        signals.append(
            make_signal(
                signal_type="PUBLIC_COMPLAINTS",
                severity="HIGH",
                description=(
                    "Publicly available complaint or "
                    "job-fraud reports were found during "
                    "company research."
                ),
                evidence=(
                    "Company research returned public "
                    "complaint or job-fraud reporting. "
                    "These reports should be treated as "
                    "reported allegations, not automatic proof."
                ),
                score=RISK_WEIGHTS[
                    "PUBLIC_COMPLAINTS"
                ],
            )
        )

    return signals


# ============================================================
# JOB VERIFICATION SIGNALS
# ============================================================

def detect_job_signals(
    job_result: dict | None,
) -> list[dict]:

    signals: list[dict] = []

    if not job_result:
        return signals

    status = normalize_text(
        job_result.get("status")
    )

    not_verified_statuses = {
        "not_found",
        "unverified",
        "unable_to_verify",
        "not independently verified",
        "not_verified",
        "unknown",
        "error",
    }

    if status in not_verified_statuses:

        signals.append(
            make_signal(
                signal_type="JOB_NOT_VERIFIED",
                severity="MEDIUM",
                description=(
                    "The exact job opportunity could not "
                    "be independently confirmed."
                ),
                evidence=(
                    "No reliable independent evidence was "
                    "returned for the exact job opportunity."
                ),
                score=RISK_WEIGHTS[
                    "JOB_NOT_VERIFIED"
                ],
            )
        )

    return signals


# ============================================================
# RISK LEVEL
# ============================================================

def risk_level(
    score: int,
) -> str:

    score = max(
        0,
        min(
            int(score),
            100,
        ),
    )

    if score >= 50:
        return "HIGH"

    if score >= 20:
        return "MEDIUM"

    return "LOW"


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk(
    signals: list[dict],
) -> dict:

    if not signals:

        return {
            "risk_score": 0,
            "risk_level": "UNABLE_TO_VERIFY",
            "signals": [],
        }

    total_score = sum(
        int(
            signal.get(
                "score",
                0,
            )
        )
        for signal in signals
    )

    total_score = min(
        max(
            total_score,
            0,
        ),
        100,
    )

    level = risk_level(
        total_score
    )

    return {
        "risk_score": total_score,
        "risk_level": level,
        "signals": signals,
    }


# ============================================================
# MAIN RISK ENGINE
# ============================================================

def assess_risk(
    text: str,
    job: Any,
    company_result: dict | None = None,
    job_result: dict | None = None,
) -> dict:

    signals: list[dict] = []

    # --------------------------------------------------------
    # 1. MESSAGE SIGNALS
    # --------------------------------------------------------

    signals.extend(
        detect_message_signals(
            text=text,
            job=job,
        )
    )

    # --------------------------------------------------------
    # 2. COMPANY SIGNALS
    # --------------------------------------------------------

    signals.extend(
        detect_company_signals(
            company_result=company_result,
            submitted_location=getattr(
                job,
                "location",
                None,
            ),
        )
    )

    # --------------------------------------------------------
    # 3. JOB SIGNALS
    # --------------------------------------------------------

    signals.extend(
        detect_job_signals(
            job_result=job_result,
        )
    )

    # --------------------------------------------------------
    # 4. REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_signals: list[dict] = []
    seen_types: set[str] = set()

    for signal in signals:

        signal_type = signal.get(
            "signal_type",
            "",
        )

        if signal_type in seen_types:
            continue

        seen_types.add(
            signal_type
        )

        unique_signals.append(
            signal
        )

    # --------------------------------------------------------
    # 5. CALCULATE FINAL RISK
    # --------------------------------------------------------

    result = calculate_risk(
        unique_signals
    )

    # --------------------------------------------------------
    # 6. SUMMARY
    # --------------------------------------------------------

    level = result[
        "risk_level"
    ]

    score = result[
        "risk_score"
    ]

    if level == "HIGH":

        summary = (
            "Multiple high-risk indicators were detected. "
            "Do not send money or sensitive information until "
            "the company, recruiter and exact opportunity "
            "have been independently verified."
        )

    elif level == "MEDIUM":

        summary = (
            "Some warning indicators were detected. "
            "Further independent verification is recommended "
            "before proceeding."
        )

    elif level == "LOW":

        summary = (
            "Only limited warning indicators were detected "
            "from the currently available evidence. "
            "This does not guarantee that the opportunity "
            "is legitimate."
        )

    else:

        summary = (
            "There is not enough evidence to produce a "
            "meaningful risk classification."
        )

    result["summary"] = summary
    result["risk_score"] = score
    result["risk_level"] = level

    return result