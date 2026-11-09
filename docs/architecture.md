# JobShield AI Architecture

## Core principle

Evidence first, deterministic checks second, LLM explanation third.

## Pipeline

1. Input
2. Extraction
3. Normalization
4. Company verification
5. Job verification
6. Domain/URL analysis
7. Risk signals
8. Risk score
9. LLM explanation
10. Report

## Agent responsibilities

### ExtractionAgent
Converts unstructured input to JobInformation.

### CompanyVerificationAgent
Checks company evidence through configured providers.

### JobVerificationAgent
Checks whether the job can be independently verified.

### RiskAgent
Combines deterministic risk rules.

### ReportAgent
Creates a user-facing evidence-based report.

## Production evolution

Replace in-memory AnalysisService storage with PostgreSQL.
Add a job queue for long-running verification.
Add SSRF-safe URL fetching.
Add source snapshots and citations.
Add authentication and per-user history.
