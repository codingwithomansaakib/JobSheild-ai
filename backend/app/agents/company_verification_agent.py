import asyncio

from app.tools.company_tools import research_company


class CompanyVerificationAgent:

    async def run(
        self,
        company_name: str | None,
        submitted_url: str | None = None,
        location: str | None = None,
    ) -> dict:

        return await research_company(
            company_name=company_name or "",
            location=location,
            website=submitted_url,
        )

    def verify(
        self,
        company_name: str | None,
        submitted_url: str | None = None,
        location: str | None = None,
    ) -> dict:
        """
        Backward-compatible synchronous method.

        The current AnalysisService calls verify().
        Internally we use the async research_company() function.
        """

        return asyncio.run(
            self.run(
                company_name=company_name,
                submitted_url=submitted_url,
                location=location,
            )
        )
