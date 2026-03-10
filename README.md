# Technical-Assessment

FastAPI service that sanitizes sensitive data, simulates an external AI response, writes an audit trail, and protects the upstream call with a circuit breaker.

## Requirements covered

- `POST /secure-inquiry`
- Redacts emails, credit cards, and SSNs / 9-digit numeric identifiers
- Simulates a 2-second AI response
- Stores the original message encrypted and the redacted message in `data/audit_log.json`
- Opens a circuit breaker after 3 consecutive AI failures and returns `Service Busy` immediately

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Example request:

```bash
curl -X POST http://localhost:8000/secure-inquiry \
  -H "Content-Type: application/json" \
  -d '{"userId":"u-123","message":"contact me at jane@example.com with SSN 123-45-6789"}'
```

To simulate AI failures, include `[fail-ai]` in the message.

## Run with Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest
```
