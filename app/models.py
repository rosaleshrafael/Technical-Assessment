from pydantic import BaseModel, Field


class SecureInquiryRequest(BaseModel):
    userId: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=10_000)


class SecureInquiryResponse(BaseModel):
    answer: str
    redactedMessage: str
    circuitBreakerOpen: bool = False

