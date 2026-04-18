"""Simple agent demo."""

from loguru import logger
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, START, END

from .logging_config import configure_logging
from .nodes import (
    node_list_tables,
    node_select_relevant_tables,
    node_get_schema,
    node_generate_query,
    node_execute_query,
    node_generate_answer,
)
from .state import AgentState


def get_model():
    logger.info("Loading model")
    llm = HuggingFacePipeline.from_model_id(
        model_id="Qwen/Qwen2.5-1.5B-Instruct",
        task="text-generation",
        pipeline_kwargs={"max_new_tokens": 1024, "temperature": 0.7},
    )
    return ChatHuggingFace(llm=llm)


def setup_db(db_path: str = "data/Chinook.db"):
    logger.info(f"Initializing database resources for {db_path}")
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def build_agent_graph(model, db, only_query: bool = False):
    """Build agent with simple linear flow."""
    graph = StateGraph(AgentState)  # ty: ignore[invalid-argument-type]

    graph.add_node("list_tables", lambda state: node_list_tables(state, db))
    graph.add_node(
        "select_tables", lambda state: node_select_relevant_tables(state, model)
    )
    graph.add_node("get_schema", lambda state: node_get_schema(state, db))
    graph.add_node("generate_query", lambda state: node_generate_query(state, model))
    graph.add_node("execute_query", lambda state: node_execute_query(state, db))
    graph.add_node("generate_answer", lambda state: node_generate_answer(state, model))

    graph.add_edge(START, "list_tables")
    graph.add_edge("list_tables", "select_tables")
    graph.add_edge("select_tables", "get_schema")
    graph.add_edge("get_schema", "generate_query")

    if only_query:
        graph.add_edge("generate_query", END)
    else:
        graph.add_edge("generate_query", "execute_query")
        graph.add_edge("execute_query", "generate_answer")
        graph.add_edge("generate_answer", END)

    return graph.compile()


def run_agent(agent, user_question: str):
    """Execute the agent with a user question.

    Args:
        agent: The compiled LangGraph agent
        user_question: What the user is asking
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
    }

    final_state = agent.invoke(initial_state)

    logger.info("Final answer: {}", final_state["final_answer"])

    return final_state


def main():
    """Main entry point."""

    configure_logging()
    model = get_model()
    db = setup_db()

    logger.info("Building graph")
    agent = build_agent_graph(model, db)

    question = "Which genre on average has the longest tracks?"
    _ = run_agent(agent, question)

    logger.info("Agent completed successfully")


if __name__ == "__main__":
    main()
