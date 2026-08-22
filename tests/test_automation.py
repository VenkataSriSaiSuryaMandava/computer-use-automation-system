import pytest
from src.schemas import CapabilityArtifact
from src.replay import DeterministicReplayEngine
from src.guardrails import SafetyGuardrail

@pytest.fixture
def loaded_artifact():
    with open("evidence/capability_artifact.json") as f:
        return CapabilityArtifact.model_validate_json(f.read())

def test_guardrail_url_allowlist():
    SafetyGuardrail.validate_url("http://127.0.0.1:8000/members/search")
    with pytest.raises(PermissionError):
        SafetyGuardrail.validate_url("https://malicious-external-site.com")

def test_guardrail_pii_sanitization():
    raw_payload = {"ssn": "987-65-4321", "balance": "$14,850.25"}
    clean_payload = SafetyGuardrail.sanitize_payload(raw_payload)
    assert clean_payload["ssn"] == "[REDACTED_SSN]"
    assert clean_payload["balance"] == "$14,850.25"

def test_replay_valid_member(loaded_artifact):
    engine = DeterministicReplayEngine(loaded_artifact)
    result = engine.replay({"member_id": "12345"})
    assert result.status == "SUCCESS"
    assert result.data["savings_balance"] == "$14,850.25"

def test_replay_business_error_not_found(loaded_artifact):
    engine = DeterministicReplayEngine(loaded_artifact)
    result = engine.replay({"member_id": "00000"})
    assert result.status == "BUSINESS_OUTCOME"
    assert result.business_code == "MEMBER_NOT_FOUND"