from typing import override

from langchain_community.utilities import SQLDatabase
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent.common.agent import BaseAgent
from agent.common.llm import LLMAdapter
from agent.common.nodes import (
    node_list_tables,
    node_select_relevant_tables,
    node_get_schema,
    node_execute_query,
    node_use_all_tables,
    should_retry_after_execution,
    node_generate_answer,
)
from agent.plan_and_solve.nodes import (
    node_generate_query_plan,
    node_generate_query_solve,
    node_correct_query_plan,
    node_correct_query_solve,
)
from agent.plan_and_solve.state import PlanAndSolveAgentState


class PlanAndSolveAgent(BaseAgent):
    def __init__(self, model: LLMAdapter, db: SQLDatabase, only_query: bool):
        self.model = model
        self.db = db
        self.only_query = only_query
        self.graph = self.build_graph(model, db, only_query)

    @override
    @staticmethod
    def build_graph(model: LLMAdapter, db: SQLDatabase, only_query: bool):
        graph = StateGraph(PlanAndSolveAgentState)  # ty: ignore[invalid-argument-type]

        graph.add_node("list_tables", lambda state: node_list_tables(state, db))
        graph.add_node(
            "select_tables", lambda state: node_select_relevant_tables(state, model)
        )
        graph.add_node("use_all_tables", lambda state: node_use_all_tables(state))
        graph.add_node("get_schema", lambda state: node_get_schema(state, db))
        graph.add_node(
            "generate_query_plan", lambda state: node_generate_query_plan(state, model)
        )
        graph.add_node(
            "generate_query_solve",
            lambda state: node_generate_query_solve(state, model),
        )
        graph.add_node("execute_query", lambda state: node_execute_query(state, db))
        graph.add_node(
            "correct_query_plan", lambda state: node_correct_query_plan(state, model)
        )
        graph.add_node(
            "correct_query_solve", lambda state: node_correct_query_solve(state, model)
        )
        graph.add_node(
            "generate_answer", lambda state: node_generate_answer(state, model)
        )

        graph.add_edge(START, "list_tables")
        graph.add_edge("list_tables", "select_tables")
        graph.add_edge("select_tables", "get_schema")
        graph.add_edge("get_schema", "generate_query_plan")
        graph.add_edge("generate_query_plan", "generate_query_solve")
        graph.add_edge("generate_query_solve", "execute_query")

        graph.add_conditional_edges(
            "execute_query",
            should_retry_after_execution,
            {
                "done": END if only_query else "generate_answer",
                "use_all_tables": "correct_query_plan",  # The planning logic should handle this
                "correct_query": "correct_query_plan",
            },
        )

        if not only_query:
            graph.add_edge("generate_answer", END)

        graph.add_edge("correct_query_plan", "correct_query_solve")
        graph.add_edge("correct_query_solve", "execute_query")

        return graph.compile()

    @override
    def get_initial_state(
        self, user_question: str, max_correction_attempts: int = 2
    ) -> PlanAndSolveAgentState:
        return {
            "user_question": user_question,
            "all_tables": [],
            "relevant_tables": [],
            "table_schemas": "",
            "generated_query": "",
            "query_result": "",
            "final_answer": "",
            "execution_error": "",
            "correction_attempts": 0,
            "max_correction_attempts": max_correction_attempts,
            "used_all_tables_fallback": False,
            "generate_query_plan": "",
        }

    @override
    def run(
        self, user_question: str, max_correction_attempts: int = 2
    ) -> PlanAndSolveAgentState:
        initial_state = self.get_initial_state(user_question, max_correction_attempts)
        final_state = self.graph.invoke(initial_state)
        return final_state
