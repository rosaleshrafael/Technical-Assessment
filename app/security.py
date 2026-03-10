import base64
import hashlib
import os
import re
from typing import Optional, Pattern

from cryptography.fernet import Fernet


class AISanitizer:
    EMAIL_PATTERN: Pattern[str] = re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        re.IGNORECASE,
    )
    CREDIT_CARD_PATTERN: Pattern[str] = re.compile(
        r"\b(?:\d[ -]*?){13,16}\b"
    )
    SSN_PATTERN: Pattern[str] = re.compile(
        r"(?<!\d)(?:\d{3}-?\d{2}-?\d{4}|\d{9})(?!\d)"
    )

    def sanitize(self, message: str) -> str:
        redacted = self.EMAIL_PATTERN.sub("<REDACTED: EMAIL>", message)
        redacted = self.CREDIT_CARD_PATTERN.sub("<REDACTED: CREDIT_CARD>", redacted)
        redacted = self.SSN_PATTERN.sub("<REDACTED: SSN>", redacted)
        return redacted


def _build_fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


class Encryptor:
    def __init__(self, secret: Optional[str] = None) -> None:
        encryption_secret = secret or os.getenv("APP_ENCRYPTION_SECRET", "dev-secret")
        self._fernet = Fernet(_build_fernet_key(encryption_secret))

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")
