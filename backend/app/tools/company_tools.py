from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Optional

from groq import Groq

from app.core.config import settings


# ============================================================
# PROMPT
# ============================================================

def build_company_research_prompt(
    company_name: str,
    location: Optional[str] = None,
    website: Optional[str] = None,
) -> str:
    """
    Build an evidence-focused research prompt.

    The LLM performs research only.
    It does NOT make the final JobShield risk decision.
    """

    location_text = location or "Not provided"
    website_text = website or "Not provided"

    return f"""
You are the web research component of JobShield AI.

Investigate the following company using current public information
available on the internet.

USER-SUBMITTED INFORMATION
--------------------------
Company Name: {company_name}
Submitted Location: {location_text}
Submitted Website: {website_text}

IMPORTANT:

You are a research and evidence extraction component.

Do NOT automatically call the company fake.

Do NOT provide a fraud probability.

Do NOT make the final JobShield risk decision.

"Not found" means "unable to verify", not necessarily fake.

Prefer:
- official company sources
- government/company registry information
- established business directories
- official careers pages
- reliable professional/business sources
- clearly identified public complaint sources

Distinguish facts from allegations.

============================================================
1. COMPANY EXISTENCE
============================================================

Find evidence that the company exists.

Determine:
- exact or closest company name
- whether the company appears to exist
- legal/company registration information if available
- company status if available

Pay special attention to statuses such as:
- Active
- Strike Off
- Struck Off
- Dormant
- Under Liquidation
- Cancelled
- Inactive

Do not infer a company status without evidence.

============================================================
2. OFFICIAL WEBSITE
============================================================

Find the company's likely official website.

Compare it with:

Submitted Website:
{website_text}

Do not invent a website.

If no official website can be confidently identified,
return null.

============================================================
3. REGISTERED / BUSINESS ADDRESS
============================================================

Find the company's independently reported address.

Pay attention to:
- registered office
- corporate office
- headquarters
- branch office
- business listing address

Compare the discovered address with:

Submitted Location:
{location_text}

IMPORTANT:

A registered office and a branch/office can legitimately be
different.

Do not call an address a mismatch merely because the company
has multiple offices.

If there is clear evidence that the submitted location does
not belong to the identified company, report a mismatch.

============================================================
4. BUSINESS PRESENCE
============================================================

Look for:
- company profiles
- business listings
- professional profiles
- government/company records
- established business sources

============================================================
5. CAREERS / JOB PRESENCE
============================================================

Search for:
- official careers page
- company job listings
- official recruitment information
- professional job postings

Do not claim the exact submitted job is genuine unless
independent evidence supports that conclusion.

============================================================
6. PUBLIC REVIEWS
============================================================

Look for publicly available:
- employee reviews
- customer reviews
- business reviews

Do not claim that every individual review is genuine.

Distinguish:
- employee reviews
- customer reviews
- business-directory ratings

============================================================
7. COMPLAINTS / SCAM REPORTS
============================================================

Search for combinations such as:

"{company_name}" scam
"{company_name}" fraud
"{company_name}" job scam
"{company_name}" recruitment scam
"{company_name}" complaints
"{company_name}" fake job

If complaints are found:
- report the source
- describe the allegation
- do not present an allegation as proven fact

============================================================
8. IDENTITY MATCHING
============================================================

Compare:

Submitted Company:
{company_name}

Submitted Location:
{location_text}

Submitted Website:
{website_text}

against independently discovered information.

Determine separately:

- company name match
- location/address match
- website match

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Do not use markdown code fences.

Use exactly this structure:

{{
  "company_name": "{company_name}",
  "company_exists": null,
  "company_status": null,
  "registered_address": null,
  "official_website": null,

  "location_found": null,
  "location_match": null,
  "website_match": null,
  "company_name_match": null,

  "business_presence": null,
  "careers_presence": null,

  "public_reviews": [],
  "complaints": [],

  "important_evidence": [],

  "sources": [
    {{
      "title": "",
      "url": "",
      "source_type": ""
    }}
  ],

  "research_summary": "",
  "overall_research_status": ""
}}

Allowed values:

company_exists:
- true
- false
- null

company_status:
- "ACTIVE"
- "STRIKE OFF"
- "STRUCK OFF"
- "DORMANT"
- "INACTIVE"
- "LIQUIDATION"
- "CANCELLED"
- "UNKNOWN"

location_found:
- true
- false
- null

location_match:
- "MATCH"
- "MISMATCH"
- "PARTIAL"
- "UNKNOWN"

website_match:
- "MATCH"
- "MISMATCH"
- "UNKNOWN"

company_name_match:
- "MATCH"
- "MISMATCH"
- "PARTIAL"
- "UNKNOWN"

overall_research_status:
- "FOUND"
- "PARTIALLY_FOUND"
- "NOT_FOUND"
- "CONFLICTING"
- "UNABLE_TO_VERIFY"

RULES FOR JSON:

- Use null when evidence is unavailable.
- Do not invent URLs.
- URLs must come from the research results.
- Keep complaint claims clearly described as allegations.
- Do not make a final fraud determination.
"""


# ============================================================
# JSON EXTRACTION
# ============================================================

def _extract_json(text: str) -> dict[str, Any]:
    """
    Extract JSON from the LLM response.

    Handles:
    - plain JSON
    - ```json ... ```
    - extra text around JSON
    """

    if not text:
        return {}

    text = text.strip()

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:
        parsed = json.loads(text)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # JSON markdown block
    # --------------------------------------------------------

    match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if match:

        try:
            parsed = json.loads(match.group(1))

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    # --------------------------------------------------------
    # Find first JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = text[start : end + 1]

        try:
            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    return {}


# ============================================================
# NORMALIZATION
# ============================================================

def _clean_string(value: Any) -> Optional[str]:

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def _normalize_status(value: Any) -> str:

    value = _clean_string(value)

    if not value:
        return "UNKNOWN"

    value = value.upper().strip()

    replacements = {
        "STRIKE_OFF": "STRIKE OFF",
        "STRIKE-OFF": "STRIKE OFF",
        "STRUCK OFF": "STRUCK OFF",
        "UNDER LIQUIDATION": "LIQUIDATION",
    }

    return replacements.get(value, value)


def _normalize_list(value: Any) -> list:

    if not isinstance(value, list):
        return []

    return value


def _normalize_sources(value: Any) -> list[dict]:

    if not isinstance(value, list):
        return []

    sources = []

    for item in value:

        if not isinstance(item, dict):
            continue

        title = _clean_string(
            item.get("title")
        )

        url = _clean_string(
            item.get("url")
        )

        source_type = _clean_string(
            item.get("source_type")
        )

        # Do not create fake sources.
        if not title and not url:
            continue

        sources.append(
            {
                "title": title or "Source",
                "url": url or "",
                "source_type": source_type or "UNKNOWN",
            }
        )

    return sources


# ============================================================
# GROQ RESEARCH
# ============================================================

def _research_company_sync(
    company_name: str,
    location: Optional[str],
    website: Optional[str],
) -> dict:

    if not settings.GROQ_API_KEY:

        return {
            "status": "ERROR",
            "company_name": company_name,
            "error": "GROQ_API_KEY is not configured.",
            "research": "",
        }

    client = Groq(
        api_key=settings.GROQ_API_KEY
    )

    prompt = build_company_research_prompt(
        company_name=company_name,
        location=location,
        website=website,
    )

    response = client.chat.completions.create(
        model=(
            settings.GROQ_MODEL
            or "openai/gpt-oss-20b"
        ),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evidence-focused "
                    "company research assistant. "
                    "Return valid JSON exactly as requested."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        tools=[
            {
                "type": "browser_search"
            }
        ],
        tool_choice="required",
        temperature=0,
        max_completion_tokens=5000,
    )

    message = response.choices[0].message

    research_text = (
        message.content or ""
    ).strip()

    structured = _extract_json(
        research_text
    )

    # --------------------------------------------------------
    # If structured JSON was returned
    # --------------------------------------------------------

    if structured:

        company_status = _normalize_status(
            structured.get("company_status")
        )

        registered_address = _clean_string(
            structured.get("registered_address")
        )

        official_website = _clean_string(
            structured.get("official_website")
        )

        company_exists = structured.get(
            "company_exists"
        )

        location_found = structured.get(
            "location_found"
        )

        location_match = _clean_string(
            structured.get("location_match")
        )

        website_match = _clean_string(
            structured.get("website_match")
        )

        company_name_match = _clean_string(
            structured.get("company_name_match")
        )

        overall_status = _clean_string(
            structured.get(
                "overall_research_status"
            )
        )

        # ----------------------------------------------------
        # Determine research status
        # ----------------------------------------------------

        final_status = (
            overall_status
            or "PARTIALLY_FOUND"
        )

        # ----------------------------------------------------
        # Preserve structured data
        # ----------------------------------------------------

        return {
            "status": "RESEARCHED",

            "company_name": (
                _clean_string(
                    structured.get(
                        "company_name"
                    )
                )
                or company_name
            ),

            "company_exists": company_exists,

            "company_status": company_status,

            "registered_address": (
                registered_address
            ),

            "official_website": (
                official_website
            ),

            "location_found": (
                location_found
            ),

            "location_match": (
                location_match
            ),

            "website_match": (
                website_match
            ),

            "company_name_match": (
                company_name_match
            ),

            "business_presence": (
                structured.get(
                    "business_presence"
                )
            ),

            "careers_presence": (
                structured.get(
                    "careers_presence"
                )
            ),

            "public_reviews": _normalize_list(
                structured.get(
                    "public_reviews"
                )
            ),

            "complaints": _normalize_list(
                structured.get(
                    "complaints"
                )
            ),

            "important_evidence": _normalize_list(
                structured.get(
                    "important_evidence"
                )
            ),

            "sources": _normalize_sources(
                structured.get(
                    "sources"
                )
            ),

            "research_summary": (
                _clean_string(
                    structured.get(
                        "research_summary"
                    )
                )
                or ""
            ),

            "overall_research_status": (
                final_status
            ),

            # Keep original response too.
            "research": research_text,

            "model": (
                settings.GROQ_MODEL
                or "openai/gpt-oss-20b"
            ),
        }

    # --------------------------------------------------------
    # Fallback if LLM did not return valid JSON
    # --------------------------------------------------------

    return {
        "status": "RESEARCHED",
        "company_name": company_name,

        "company_exists": None,
        "company_status": "UNKNOWN",
        "registered_address": None,
        "official_website": None,

        "location_found": None,
        "location_match": "UNKNOWN",
        "website_match": "UNKNOWN",
        "company_name_match": "UNKNOWN",

        "business_presence": None,
        "careers_presence": None,

        "public_reviews": [],
        "complaints": [],
        "important_evidence": [],
        "sources": [],

        "research_summary": (
            "The research provider returned "
            "unstructured research text. "
            "Structured company fields could not "
            "be reliably extracted."
        ),

        "overall_research_status": (
            "PARTIALLY_FOUND"
        ),

        "research": research_text,

        "model": (
            settings.GROQ_MODEL
            or "openai/gpt-oss-20b"
        ),
    }


# ============================================================
# PUBLIC ASYNC FUNCTION
# ============================================================

async def research_company(
    company_name: str,
    location: Optional[str] = None,
    website: Optional[str] = None,
) -> dict:
    """
    Research an arbitrary company asynchronously.

    The synchronous Groq SDK call runs in a worker thread
    so it does not block FastAPI's event loop.
    """

    company_name = (
        company_name.strip()
        if company_name
        else ""
    )

    if not company_name:

        return {
            "status": "UNABLE_TO_VERIFY",
            "company_name": "",
            "research": "",
            "error": (
                "Company name was not provided."
            ),
        }

    try:

        return await asyncio.to_thread(
            _research_company_sync,
            company_name,
            location,
            website,
        )

    except Exception as exc:

        return {
            "status": "ERROR",
            "company_name": company_name,
            "research": "",
            "error": str(exc),
        }