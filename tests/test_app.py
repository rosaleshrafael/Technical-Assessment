import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.audit import AuditRepository
from app.circuit_breaker import CircuitBreaker
from app.security import Encryptor


def build_client(tmp_path: Path) -> TestClient:
    main.audit_repository = AuditRepository(str(tmp_path / "audit_log.json"))
    main.encryptor = Encryptor("test-secret")
    main.circuit_breaker = CircuitBreaker(recovery_timeout_seconds=1)
    main.ai_client.delay_seconds = 0
    return TestClient(main.app)


def test_secure_inquiry_redacts_and_logs(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    response = client.post(
        "/secure-inquiry",
        json={
            "userId": "user-1",
            "message": "Email me at test@example.com with card 4111 1111 1111 1111 and SSN 123-45-6789",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Generated Answer."
    assert "<REDACTED: EMAIL>" in body["redactedMessage"]
    assert "<REDACTED: CREDIT_CARD>" in body["redactedMessage"]
    assert "<REDACTED: SSN>" in body["redactedMessage"]

    log_entries = json.loads((tmp_path / "audit_log.json").read_text(encoding="utf-8"))
    assert len(log_entries) == 1
    assert log_entries[0]["redactedMessage"] == body["redactedMessage"]
    assert "test@example.com" not in log_entries[0]["encryptedMessage"]


def test_circuit_breaker_opens_after_three_failures(tmp_path: Path) -> None:
    client = build_client(tmp_path)
    payload = {"userId": "user-2", "message": "[fail-ai] force failure"}

    for _ in range(3):
        response = client.post("/secure-inquiry", json=payload)
        assert response.status_code == 503
        assert response.json()["detail"] == "Service Busy"

    response = client.post("/secure-inquiry", json=payload)
    assert response.status_code == 200
    assert response.json()["answer"] == "Service Busy"
    assert response.json()["circuitBreakerOpen"] is True
