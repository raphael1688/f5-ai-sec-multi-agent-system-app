from __future__ import annotations

from app.memory import ConversationMemoryStore, ConversationTurn


def test_memory_store_forget_removes_conversation_turns() -> None:
    store = ConversationMemoryStore()
    turn = ConversationTurn(
        trace_id="trace-1",
        user_request="request",
        final_answer="answer",
        route="advisor_workflow",
        recommended_product="Meridian Balanced Fund",
        guardrail_status="clear",
    )

    store.append("conversation-1", turn)

    assert store.get_recent_turns("conversation-1") == [turn]
    assert store.forget("conversation-1") is True
    assert store.get_recent_turns("conversation-1") == []
    assert store.forget("conversation-1") is False
