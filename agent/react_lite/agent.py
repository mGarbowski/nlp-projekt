from typing import override

from langchain_community.utilities import SQLDatabase
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent.common.agent import BaseAgent
from agent.common.llm import LLMAdapter
from agent.common.nodes import (
    node_execute_query,
    node_generate_answer,
    node_get_schema,
    node_list_tables,
    node_select_relevant_tables,
    node_use_all_tables,
)
from agent.react_lite.nodes import (
    node_generate_react_action,
    node_record_react_observation,
    should_continue_react,
)
from agent.react_lite.state import ReactLiteAgentState


class ReactLiteAgent(BaseAgent):
    def __init__(self, model: LLMAdapter, db: SQLDatabase, only_query: bool):
        self.model = model
        self.db = db
        self.only_query = only_query
        self.graph = self.build_graph(model, db, only_query)

    @override
    @staticmethod
    def build_graph(model: LLMAdapter, db: SQLDatabase, only_query: bool):
        graph = StateGraph(ReactLiteAgentState)  # ty: ignore[invalid-argument-type]

        graph.add_node("list_tables", lambda state: node_list_tables(state, db))
        graph.add_node(
            "select_tables", lambda state: node_select_relevant_tables(state, model)
        )
        graph.add_node("get_schema", lambda state: node_get_schema(state, db))
        graph.add_node("use_all_tables", lambda state: node_use_all_tables(state))
        graph.add_node(
            "generate_react_action",
            lambda state: node_generate_react_action(state, model),
        )
        graph.add_node("execute_query", lambda state: node_execute_query(state, db))
        graph.add_node(
            "record_observation", lambda state: node_record_react_observation(state)
        )
        graph.add_node(
            "generate_answer", lambda state: node_generate_answer(state, model)
        )

        graph.add_edge(START, "list_tables")
        graph.add_edge("list_tables", "select_tables")
        graph.add_edge("select_tables", "get_schema")
        graph.add_edge("get_schema", "generate_react_action")
        graph.add_edge("generate_react_action", "execute_query")
        graph.add_edge("execute_query", "record_observation")

        graph.add_conditional_edges(
            "record_observation",
            should_continue_react,
            {
                "done": END if only_query else "generate_answer",
                "retry": "generate_react_action",
                "use_all_tables": "use_all_tables",
            },
        )

        graph.add_edge("use_all_tables", "get_schema")

        if not only_query:
            graph.add_edge("generate_answer", END)

        return graph.compile()

    @override
    def get_initial_state(
        self, user_question: str, max_correction_attempts: int = 2
    ) -> ReactLiteAgentState:
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
            "current_thought": "",
            "react_history": [],
        }

    @override
    def run(
        self, user_question: str, max_correction_attempts: int = 2
    ) -> ReactLiteAgentState:
        initial_state = self.get_initial_state(user_question, max_correction_attempts)
        final_state = self.graph.invoke(initial_state)
        return final_state
