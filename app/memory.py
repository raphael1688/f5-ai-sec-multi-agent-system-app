# Copyright F5, Inc. 2026
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from dataclasses import dataclass, field

from app.models import GuardrailStatus


@dataclass
class ConversationTurn:
    trace_id: str
    user_request: str
    final_answer: str
    route: str
    recommended_product: str | None
    guardrail_status: GuardrailStatus
    tool_names: list[str] = field(default_factory=list)


class ConversationMemoryStore:
    def __init__(self, *, max_turns_per_conversation: int = 12) -> None:
        self._max_turns_per_conversation = max_turns_per_conversation
        self._turns_by_conversation_id: dict[str, list[ConversationTurn]] = {}

    def get_recent_turns(self, conversation_id: str, *, limit: int = 6) -> list[ConversationTurn]:
        turns = self._turns_by_conversation_id.get(conversation_id, [])
        return list(turns[-limit:])

    def append(self, conversation_id: str, turn: ConversationTurn) -> None:
        turns = self._turns_by_conversation_id.setdefault(conversation_id, [])
        turns.append(turn)
        if len(turns) > self._max_turns_per_conversation:
            del turns[: len(turns) - self._max_turns_per_conversation]

    def forget(self, conversation_id: str) -> bool:
        return self._turns_by_conversation_id.pop(conversation_id, None) is not None
