# JobShield AI

Evidence-based AI assistant for analyzing job and internship opportunities.

> JobShield AI does **not** declare a company fraudulent merely because an LLM says so.
> It extracts claims, collects available evidence, runs deterministic risk checks, and
> uses an LLM only to explain the evidence.

## Current MVP

- FastAPI backend
- React + Vite frontend
- Text analysis
- PDF text extraction
- Pydantic structured job schema
- Deterministic risk engine
- Evidence and risk-signal models
- Optional PostgreSQL via Docker Compose
- Optional OpenAI-compatible LLM extraction/reasoning
- URL/domain analysis
- Email/domain mismatch detection
- Payment/fee detection
- Basic tests
- Dockerfiles
- Clear extension points for real company/job verification APIs

## Architecture

Frontend -> FastAPI -> Extraction -> Verification Tools -> Risk Engine -> LLM Explanation -> Report

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 3. PostgreSQL (optional for the initial MVP)

```bash
docker compose up -d postgres
```

Set DATABASE_URL in backend/.env.

## LLM configuration

The MVP works without an LLM by using deterministic extraction/rules.

For LLM features, set:

```env
GROQ_API_KEY=your_key
GROQ_BASE_URL=https://api.openai.com/v1
GROQ_MODEL=your_model
```

The application uses an OpenAI-compatible HTTP interface so the provider can be changed later.

## API

- GET `/api/v1/health`
- POST `/api/v1/analyses`
- POST `/api/v1/analyses/{analysis_id}/files`
- POST `/api/v1/analyses/{analysis_id}/run`
- GET `/api/v1/analyses/{analysis_id}`
- GET `/api/v1/analyses/{analysis_id}/report`

## Safety

This project intentionally separates:
- extracted facts
- external evidence
- deterministic risk signals
- LLM explanation

Do not expose arbitrary server-side URL fetching without SSRF protections in production.
Do not store uploaded documents forever without a retention policy.
Do not send sensitive user documents to an LLM provider without appropriate consent and data controls.

## Roadmap

1. Complete the local MVP.
2. Add real company verification.
3. Add official job-page verification.
4. Add OCR/vision processing.
5. Add authentication.
6. Add asynchronous jobs/queues.
7. Add production SSRF-safe URL fetching.
8. Add evidence citations and source snapshots.
9. Deploy.
