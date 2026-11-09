from app.agents.extraction_agent import ExtractionAgent
from app.tools.document_tools import extract_pdf_text


class ExtractionService:
    def __init__(self):
        self.agent = ExtractionAgent()

    def extract(self, text: str, source_url: str | None = None, pdf_path: str | None = None):
        if pdf_path:
            text = extract_pdf_text(pdf_path)
        return self.agent.extract(text, source_url), text
