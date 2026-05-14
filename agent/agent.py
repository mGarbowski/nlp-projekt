"""Simple agent demo."""

import argparse

from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langgraph.graph import StateGraph, START, END
from loguru import logger

from agent.modes import ReasoningMode
from agent.plan_and_solve import build_plan_and_solve_agent
from .logging_config import configure_logging
from .nodes import (
    node_correct_query,
    node_execute_query,
    node_generate_answer,
    node_generate_query,
    node_get_schema,
    node_list_tables,
    node_select_relevant_tables,
    node_use_all_tables,
    should_retry_after_execution,
)
from .state import BaseAgentState, ReasoningModeAgentState


def get_model() -> BaseChatModel:
    logger.info("Loading model")
    llm = HuggingFacePipeline.from_model_id(
        model_id="Qwen/Qwen2.5-1.5B-Instruct",
        task="text-generation",
        pipeline_kwargs={"max_new_tokens": 1024, "temperature": 0.3},
    )
    return ChatHuggingFace(llm=llm)


def setup_db(db_path: str = "data/Chinook.db") -> SQLDatabase:
    logger.info(f"Initializing database resources for {db_path}")
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def build_agent_graph(
    model: BaseChatModel,
    db: SQLDatabase,
    reasoning_mode: ReasoningMode,
    only_query: bool = False,
):
    # TODO refactor COT variant
    match reasoning_mode:
        case ReasoningMode.PLAN_AND_SOLVE:
            return build_plan_and_solve_agent(model, db, only_query)
        case _:
            graph = StateGraph(BaseAgentState)  # ty: ignore[invalid-argument-type]

            def list_tables_node(state: BaseAgentState):
                return node_list_tables(state, db)

            def select_tables_node(state: BaseAgentState):
                return node_select_relevant_tables(state, model)

            def get_schema_node(state: BaseAgentState):
                return node_get_schema(state, db)

            def generate_query_node(state: ReasoningModeAgentState):
                return node_generate_query(state, model)

            def execute_query_node(state: BaseAgentState):
                return node_execute_query(state, db)

            def correct_query_node(state: BaseAgentState):
                return node_correct_query(state, model)

            def generate_answer_node(state: BaseAgentState):
                return node_generate_answer(state, model)

            def use_all_tables_node(state: BaseAgentState):
                return node_use_all_tables(state)

            graph.add_node("list_tables", list_tables_node)
            graph.add_node("select_tables", select_tables_node)
            graph.add_node("get_schema", get_schema_node)
            graph.add_node("generate_query", generate_query_node)
            graph.add_node("execute_query", execute_query_node)
            graph.add_node("correct_query", correct_query_node)
            graph.add_node("generate_answer", generate_answer_node)
            graph.add_node("use_all_tables", use_all_tables_node)

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


# TODO refactor different variants
def run_agent(
    agent,
    user_question: str,
    max_correction_attempts: int = 2,
    reasoning_mode: ReasoningMode = ReasoningMode.BASE,
):
    """Execute the agent with a user question.

    Args:
        agent: The compiled LangGraph agent
        user_question: What the user is asking
        max_correction_attempts: How many self-correction retries to allow
    """

    logger.info("Starting agent run")
    logger.info(f"User question: {user_question}")

    initial_state = {
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
        "reasoning_mode": reasoning_mode,
        "reasoning_trace": "",
    }

    final_state = agent.invoke(initial_state)

    logger.info("Final query: {}", final_state["generated_query"])
    if final_state["final_answer"]:
        logger.info("Final answer: {}", final_state["final_answer"])
    if final_state["execution_error"]:
        logger.warning("Final execution error: {}", final_state["execution_error"])

    return final_state


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reasoning-mode",
        type=str,
        choices=["none", "cot", "plan_and_solve", "react"],
        default="none",
    )
    args = parser.parse_args()

    configure_logging()
    model = get_model()
    db = setup_db()

    logger.info("Building graph")
    reasoning_mode = ReasoningMode.from_string(args.reasoning_mode)
    agent = build_agent_graph(model, db, reasoning_mode)

    question = "Which genre on average has the longest tracks?"
    _ = run_agent(agent, question, reasoning_mode)

    logger.info("Agent completed successfully")


if __name__ == "__main__":
    main()
