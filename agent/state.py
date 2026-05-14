"""State of the agent passed between nodes."""

from typing import TypedDict

from .modes import ReasoningMode


class BaseAgentState(TypedDict):
    user_question: str
    all_tables: list[str]
    relevant_tables: list[str]
    table_schemas: str
    generated_query: str
    query_result: str
    final_answer: str
    execution_error: str
    correction_attempts: int
    max_correction_attempts: int
    used_all_tables_fallback: bool


# TODO refactor
class ReasoningModeAgentState(BaseAgentState):
    reasoning_mode: ReasoningMode
    reasoning_trace: str


class PSAgentState(BaseAgentState):
    generate_query_plan: str
