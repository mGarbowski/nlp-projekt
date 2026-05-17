from typing import TypedDict

from agent.common.state import BaseAgentState


class ReactLiteHistoryEntry(TypedDict):
    thought: str
    action: str
    observation: str


class ReactLiteAgentState(BaseAgentState):
    current_thought: str
    react_history: list[ReactLiteHistoryEntry]
