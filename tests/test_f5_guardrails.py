from __future__ import annotations

from app.f5_ai_security_client import F5AISecurityChatClient
from app.models import SecurityEvent
from app.workflow import ProcurementWorkflowService


def test_f5_guardrail_payload_parser_accepts_cai_error_shape() -> None:
    parsed = F5AISecurityChatClient._extract_guardrail_result_from_payload(
        {
            "error": {
                "message": "blocked by policy",
                "cai_error": {
                    "outcome": "blocked",
                    "scanner_results": [{"scanner": "demo", "result": "blocked"}],
                    "analysis": {"reason": "demo"},
                },
            }
        }
    )

    assert parsed is not None
    assert parsed.outcome == "blocked"
    assert parsed.message == "blocked by policy"
    assert parsed.scanner_results == [{"scanner": "demo", "result": "blocked"}]
    assert parsed.analysis == {"reason": "demo"}


def test_response_guardrail_events_are_f5_only() -> None:
    events = [
        SecurityEvent(code="external_payload_redacted", severity="blocked", message="local control"),
        SecurityEvent(code="invalid_a2a_signature", severity="blocked", message="local control"),
        SecurityEvent(code="f5_guardrails_blocked", severity="blocked", message="F5 Guardrails blocked"),
    ]

    filtered = ProcurementWorkflowService._f5_guardrail_events(events)

    assert [event.code for event in filtered] == ["f5_guardrails_blocked"]
