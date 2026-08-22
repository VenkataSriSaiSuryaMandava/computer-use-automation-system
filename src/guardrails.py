import re
from urllib.parse import urlparse
from typing import Dict, Any

ALLOWED_HOSTS = ["localhost:8000", "127.0.0.1:8000", "corebank.internal.net"]

PII_PATTERNS = [
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), "[REDACTED_SSN]"),
    (re.compile(r'\b(?:\d[ -]*?){13,16}\b'), "[REDACTED_CARD]"),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'), "[REDACTED_EMAIL]")
]

class SafetyGuardrail:
    @staticmethod
    def validate_url(url: str):
        parsed = urlparse(url)
        host = parsed.netloc or parsed.path.split('/')[0]
        if host not in ALLOWED_HOSTS:
            raise PermissionError(f"Security Policy Violation: Host '{host}' is not in the institutional allowlist.")

    @staticmethod
    def sanitize_string(text: str) -> str:
        if not text:
            return text
        for pattern, replacement in PII_PATTERNS:
            text = pattern.sub(replacement, text)
        return text

    @staticmethod
    def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in payload.items():
            if isinstance(v, str):
                sanitized[k] = SafetyGuardrail.sanitize_string(v)
            elif isinstance(v, dict):
                sanitized[k] = SafetyGuardrail.sanitize_payload(v)
            elif isinstance(v, list):
                sanitized[k] = [SafetyGuardrail.sanitize_string(i) if isinstance(i, str) else i for i in v]
            else:
                sanitized[k] = v
        return sanitized

    @staticmethod
    def is_action_permitted(is_reversible: bool, user_authorized: bool = False) -> bool:
        if not is_reversible and not user_authorized:
            return False
        return True