# JobShield API

## Health

GET /api/v1/health

## Create analysis

POST /api/v1/analyses

```json
{
  "text": "Company: Example Tech\nRole: Python Intern",
  "source_url": "https://example.com/jobs/python"
}
```

## Run

POST /api/v1/analyses/{analysis_id}/run

## Result

GET /api/v1/analyses/{analysis_id}

## Report

GET /api/v1/analyses/{analysis_id}/report

## File upload

POST /api/v1/analyses/{analysis_id}/files
multipart/form-data
