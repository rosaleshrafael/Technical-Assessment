import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock


class AuditRepository:
    def __init__(self, file_path: str = "data/audit_log.json") -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")
        self._lock = Lock()

    def append_log(self, user_id: str, encrypted_message: str, redacted_message: str) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "userId": user_id,
            "encryptedMessage": encrypted_message,
            "redactedMessage": redacted_message,
        }

        with self._lock:
            records = json.loads(self.file_path.read_text(encoding="utf-8"))
            records.append(entry)
            self.file_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

