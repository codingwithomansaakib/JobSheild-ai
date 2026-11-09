from urllib.parse import urlparse


def extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    value = url if "://" in url else f"https://{url}"
    parsed = urlparse(value)
    return parsed.hostname.lower() if parsed.hostname else None


def email_domain(email: str | None) -> str | None:
    if not email or "@" not in email:
        return None
    return email.rsplit("@", 1)[1].lower().strip()


def domains_match(company_domain: str | None, recruiter_email: str | None) -> bool | None:
    if not company_domain or not recruiter_email:
        return None
    return email_domain(recruiter_email) == company_domain
