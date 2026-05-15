from typing import override

from langchain_community.utilities import SQLDatabase
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent.chain_of_thought.nodes import node_generate_query_cot
from agent.chain_of_thought.state import ChainOfThoughtAgentState
from agent.common.agent import BaseAgent
from agent.common.llm import LLMAdapter
from agent.common.nodes import (
    node_list_tables,
    node_select_relevant_tables,
    node_get_schema,
    node_execute_query,
    node_correct_query,
    node_generate_answer,
    node_use_all_tables,
    should_retry_after_execution,
)


class ChainOfThoughtAgent(BaseAgent):
    def __init__(self, model: LLMAdapter, db: SQLDatabase, only_query):
        self.model = model
        self.db = db
        self.only_query = only_query
        self.graph = self.build_graph(model, db, only_query)

    @override
    @staticmethod
    def build_graph(model: LLMAdapter, db: SQLDatabase, only_query: bool):
        graph = StateGraph(ChainOfThoughtAgentState)  # ty: ignore[invalid-argument-type]

        graph.add_node("list_tables", lambda state: node_list_tables(state, db))
        graph.add_node(
            "select_tables", lambda state: node_select_relevant_tables(state, model)
        )
        graph.add_node("get_schema", lambda state: node_get_schema(state, db))
        graph.add_node(
            "generate_query", lambda state: node_generate_query_cot(state, model)
        )
        graph.add_node("execute_query", lambda state: node_execute_query(state, db))
        graph.add_node("correct_query", lambda state: node_correct_query(state, model))
        graph.add_node(
            "generate_answer", lambda state: node_generate_answer(state, model)
        )
        graph.add_node("use_all_tables", lambda state: node_use_all_tables(state))

        graph.add_edge(START, "list_tables")
        graph.add_edge("list_tables", "select_tables")
        graph.add_edge("select_tables", "get_schema")
        graph.add_edge("get_schema", "generate_query")
        graph.add_edge("generate_query", "execute_query")

        graph.add_conditional_edges(
            "execute_query",
            should_retry_after_execution,
            {
                "correct_query": "correct_query",
                "use_all_tables": "use_all_tables",
                "done": "generate_answer" if not only_query else END,
            },
        )

        graph.add_edge("use_all_tables", "get_schema")
        graph.add_edge("correct_query", "execute_query")

        if not only_query:
            graph.add_edge("generate_answer", END)

        return graph.compile()

    @override
    def get_initial_state(
        self, user_question: str, max_correction_attempts: int = 2
    ) -> ChainOfThoughtAgentState:
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
            "reasoning_trace": "",
        }

    @override
    def run(self, user_question: str) -> ChainOfThoughtAgentState:
        initial_state = self.get_initial_state(user_question)
        final_state = self.graph.invoke(initial_state)
        return final_state
