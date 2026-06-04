# API Documentation

Base URL: `http://127.0.0.1:8000`

## GET /health

```json
{ "status": "ok", "version": "1.0.0", "ml_provider": "mock" }
```

## POST /analyze

**Request**

```json
{
  "code": "import os\nos.system(input())",
  "language": "python",
  "filename": null
}
```

**Response**

```json
{
  "report_id": "uuid",
  "risk_score": 72,
  "severity": "HIGH",
  "findings": [],
  "summary": "...",
  "recommendations": [],
  "ml_score": {
    "risk_probability": 0.65,
    "suspicious_score": 0.65,
    "is_suspicious": true,
    "provider": "mock"
  },
  "language": "python",
  "latency_seconds": 0.12
}
```

## POST /upload

Multipart form: `file` (UTF-8 source). Optional query: `language`.

Returns `{ "report_id", "filename", "message" }`.

## GET /report/{id}

Returns full stored report payload.

## GET /reports

List report summaries.

## GET /report/{id}/download?format=json|markdown|pdf

Download report artifact.
