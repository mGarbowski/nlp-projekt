"""Simple agent demo."""

from loguru import logger
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, START, END
from torch.cuda import graph

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
from .state import AgentState


def get_model():
    logger.info("Loading model")
    llm = HuggingFacePipeline.from_model_id(
        model_id="Qwen/Qwen2.5-1.5B-Instruct",
        task="text-generation",
        pipeline_kwargs={"max_new_tokens": 1024, "temperature": 0.3},
    )
    return ChatHuggingFace(llm=llm)


def setup_db(db_path: str = "data/Chinook.db"):
    logger.info(f"Initializing database resources for {db_path}")
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def build_agent_graph(model, db, only_query: bool = False):
    graph = StateGraph(AgentState)

    def list_tables_node(state: AgentState):
        return node_list_tables(state, db)

    def select_tables_node(state: AgentState):
        return node_select_relevant_tables(state, model)

    def get_schema_node(state: AgentState):
        return node_get_schema(state, db)

    def generate_query_node(state: AgentState):
        return node_generate_query(state, model)

    def execute_query_node(state: AgentState):
        return node_execute_query(state, db)

    def correct_query_node(state: AgentState):
        return node_correct_query(state, model)

    def generate_answer_node(state: AgentState):
        return node_generate_answer(state, model)

    def use_all_tables_node(state: AgentState):
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


def run_agent(agent, user_question: str, max_correction_attempts: int = 2):
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
