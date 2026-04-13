from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.graph import StateGraph, START, END

from .nodes import (
    node_list_tables,
    node_select_relevant_tables,
    node_get_schema,
    node_generate_query,
    node_execute_query,
    node_generate_answer,
)
from .state import AgentState


def setup():
    """Set up the model, database, and tools."""

    # Initialize the LLM
    model = init_chat_model(
        "Qwen/Qwen2.5-3B-Instruct",
        model_provider="huggingface",
        temperature=0.7,
        max_tokens=1024,
    )

    # Load the SQLite database
    db = SQLDatabase.from_uri("sqlite:///./data/Chinook.db")

    # Create tools from the database
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()

    return model, db, tools


def build_agent_graph(model, db):
    # Create a new graph
    graph = StateGraph(AgentState)  # ty: ignore[invalid-argument-type]

    # Add nodes (each node is a function + a name)
    # We use lambda to pass db/model since nodes only receive state by default
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
    graph.add_edge("generate_query", "execute_query")
    graph.add_edge("execute_query", "generate_answer")
    graph.add_edge("generate_answer", END)

    # Compile the graph into a runnable agent
    return graph.compile()


def run_agent(agent, user_question: str):
    """
    Execute the agent with a user question.

    Args:
        agent: The compiled LangGraph agent
        user_question: What the user is asking
    """

    print("=" * 70)
    print(f"USER QUESTION: {user_question}")
    print("=" * 70)

    # Create initial state with just the question
    initial_state = {
        "user_question": user_question,
        "all_tables": [],
        "relevant_tables": [],
        "table_schemas": "",
        "generated_query": "",
        "query_result": "",
        "final_answer": "",
    }

    # Run the agent
    # invoke() runs the graph and returns the final state
    final_state = agent.invoke(initial_state)

    # Display the answer
    print("\n" + "=" * 70)
    print("FINAL ANSWER:")
    print("=" * 70)
    print(final_state["final_answer"])
    print("=" * 70)

    return final_state


def main():
    """Main entry point."""

    print("Initializing SQL Agent...")
    model, db, tools = setup()

    print("Building graph...")
    agent = build_agent_graph(model, db)

    # Test with a question
    question = "Which genre on average has the longest tracks?"
    _ = run_agent(agent, question)

    print("\nAgent completed successfully!")


if __name__ == "__main__":
    main()
