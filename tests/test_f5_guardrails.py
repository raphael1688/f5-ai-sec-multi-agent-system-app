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


def test_orchestrator_out_of_scope_route_is_honored() -> None:
    class FakeClient:
        def complete(self, **kwargs):
            return {
                "role": "assistant",
                "content": (
                    '{"route":"out_of_scope","plan_summary":"Greeting only.",'
                    '"steps":[{"tool_candidates":["mcp_market_product_search"]}],'
                    '"decision_notes":["No tools needed."],'
                    '"out_of_scope_response":"Hi, I can help with advisor workflows."}'
                ),
                "_meta": {"guardrail_outcome": "clear"},
            }

    service = ProcurementWorkflowService.__new__(ProcurementWorkflowService)
    service.client = FakeClient()

    plan = service._call_orchestrator(
        trace_id="trace-1",
        conversation_id="conversation-1",
        user_request="hi",
        conversation_history=[],
        scenario_flags={},
        prompt_mode="weak",
        model_interactions=[],
    )

    assert plan["route"] == "out_of_scope"
    assert plan["steps"] == []
    assert "advisor workflows" in plan["out_of_scope_response"]


def test_mock_orchestrator_routes_greeting_out_of_scope() -> None:
    messages = [
        {"role": "system", "content": "test"},
        {"role": "user", "content": '{"request":"hi"}'},
    ]
    client = F5AISecurityChatClient.__new__(F5AISecurityChatClient)
    client._counter = 0

    response = client._mock_complete(
        agent_name="advisor_orchestrator",
        messages=messages,
        tools=None,
        tool_choice=None,
    )

    assert '"route": "out_of_scope"' in response["content"]
    assert "Advisor Assistant" in response["content"]
