from urllib.parse import urlparse


SUSPICIOUS_TERMS = {
    "verify-account",
    "registration-fee",
    "urgent",
    "pay-now",
    "claim-prize",
    "telegram",
    "whatsapp",
}


def analyze_url(url: str | None) -> dict:
    if not url:
        return {
            "provided": False,
            "https": None,
            "domain": None,
            "suspicious_pattern": False,
            "reasons": [],
        }

    value = url if "://" in url else f"https://{url}"
    parsed = urlparse(value)
    lower = value.lower()

    reasons = []
    if parsed.scheme != "https":
        reasons.append("URL does not use HTTPS.")
    if any(term in lower for term in SUSPICIOUS_TERMS):
        reasons.append("URL contains a pattern that warrants manual verification.")

    return {
        "provided": True,
        "https": parsed.scheme == "https",
        "domain": parsed.hostname.lower() if parsed.hostname else None,
        "suspicious_pattern": bool(reasons),
        "reasons": reasons,
    }
