from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Optional


@dataclass
class BreakerState:
    consecutive_failures: int = 0
    opened_at: Optional[datetime] = None


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout_seconds: int = 10) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_seconds)
        self._state = BreakerState()
        self._lock = Lock()

    def allow_request(self) -> bool:
        with self._lock:
            if self._state.opened_at is None:
                return True

            if datetime.now(timezone.utc) - self._state.opened_at >= self.recovery_timeout:
                self._state.opened_at = None
                return True

            return False

    def record_success(self) -> None:
        with self._lock:
            self._state.consecutive_failures = 0
            self._state.opened_at = None

    def record_failure(self) -> None:
        with self._lock:
            self._state.consecutive_failures += 1
            if self._state.consecutive_failures >= self.failure_threshold:
                self._state.opened_at = datetime.now(timezone.utc)
