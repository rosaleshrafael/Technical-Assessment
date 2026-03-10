from fastapi import FastAPI, HTTPException
from typing import Dict

from app.ai_client import MockAIClient, MockAIError
from app.audit import AuditRepository
from app.circuit_breaker import CircuitBreaker
from app.models import SecureInquiryRequest, SecureInquiryResponse
from app.security import AISanitizer, Encryptor

app = FastAPI(title="Secure Inquiry API", version="1.0.0")

sanitizer = AISanitizer()
encryptor = Encryptor()
audit_repository = AuditRepository()
ai_client = MockAIClient()
circuit_breaker = CircuitBreaker()


@app.get("/health")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/secure-inquiry", response_model=SecureInquiryResponse)
async def secure_inquiry(payload: SecureInquiryRequest) -> SecureInquiryResponse:
    redacted_message = sanitizer.sanitize(payload.message)
    encrypted_message = encryptor.encrypt(payload.message)
    audit_repository.append_log(payload.userId, encrypted_message, redacted_message)

    if not circuit_breaker.allow_request():
        return SecureInquiryResponse(
            answer="Service Busy",
            redactedMessage=redacted_message,
            circuitBreakerOpen=True,
        )

    try:
        answer = await ai_client.generate_answer(redacted_message)
    except MockAIError as exc:
        circuit_breaker.record_failure()
        raise HTTPException(status_code=503, detail="Service Busy") from exc

    circuit_breaker.record_success()
    return SecureInquiryResponse(
        answer=answer,
        redactedMessage=redacted_message,
        circuitBreakerOpen=False,
    )
