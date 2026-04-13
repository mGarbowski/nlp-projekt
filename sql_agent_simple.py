"""
A simple, linear SQL agent using LangGraph for learning purposes.

LangGraph Concepts:
1. StateGraph: A graph structure for your agent's workflow
2. Nodes: Functions that process state and return updates
3. State: A shared dictionary that flows through nodes (like a relay baton)
4. Edges: Connections between nodes (flow of execution)
5. MessagesState: LangChain's built-in state for conversation history

The flow:
  user question → list tables → select relevant tables → get schema → 
  generate SQL → execute query → generate answer → output

Each step receives the current state, does some work, and returns updates.
"""

import os
from typing import TypedDict
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END

from utils import parse_chat_template_text


# ============================================================================
# STEP 1: Define our State
# ============================================================================
class SQLAgentState(TypedDict):
    """
    The 'bag' that travels through our graph, accumulating information.
    
    - user_question: The user's natural language question
    - all_tables: List of table names in database
    - relevant_tables: Tables we think are relevant to the question
    - table_schemas: SQL schema definitions for relevant tables
    - generated_query: The SQL query we generated
    - query_result: Results from running the query
    - final_answer: The answer we present to the user
    """
    user_question: str
    all_tables: list[str]
    relevant_tables: list[str]
    table_schemas: str
    generated_query: str
    query_result: str
    final_answer: str


# ============================================================================
# STEP 2: Initialize model, database, and tools
# ============================================================================
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


# ============================================================================
# STEP 3: Define node functions (the actual work happens here)
# ============================================================================



def node_list_tables(state: SQLAgentState, db: SQLDatabase) -> dict:
    """
    Node 1: List all available tables.
    
    INPUT: user_question
    OUTPUT: all_tables
    """
    print("\n[Node 1] Listing all tables...")
    tables = db.get_usable_table_names()
    print(f"  Found tables: {tables}")
    
    return {
        "all_tables": tables
    }


def node_select_relevant_tables(state: SQLAgentState, model) -> dict:
    """
    Node 2: Use LLM to select which tables are relevant to the question.
    
    INPUT: user_question, all_tables
    OUTPUT: relevant_tables
    """
    print("\n[Node 2] Selecting relevant tables...")
    
    prompt = f"""
Given this question: "{state['user_question']}"

These tables are available: {', '.join(state['all_tables'])}

Which tables would you need to query to answer the question?
Return ONLY a comma-separated list of table names, nothing else.
Example: "Artist,Album,Genre"
"""
    
    response = model.invoke([HumanMessage(content=prompt)])
    response_messages = parse_chat_template_text(response.content)
    table_names = response_messages[-1]["message"].split(",")
    table_names = [t.strip() for t in table_names]

    print(f"  Selected tables: {table_names}")
    
    return {
        "relevant_tables": table_names
    }


def node_get_schema(state: SQLAgentState, db: SQLDatabase) -> dict:
    """
    Node 3: Fetch the schema (column names, types) for relevant tables.
    
    INPUT: relevant_tables
    OUTPUT: table_schemas
    """
    print("\n[Node 3] Getting table schemas...")
    
    # Build schema string for the selected tables
    schemas = []
    for table_name in state["relevant_tables"]:
        try:
            schema = db.get_table_info([table_name])
            schemas.append(schema)
        except Exception as e:
            print(f"  Warning: Could not get schema for {table_name}: {e}")
    
    schema_text = "\n\n".join(schemas)
    print(f"  Schema retrieved for tables: {state['relevant_tables']}")
    
    return {
        "table_schemas": schema_text
    }


def node_generate_query(state: SQLAgentState, model) -> dict:
    """
    Node 4: Use LLM to generate a SQL query based on the question and schema.
    
    INPUT: user_question, table_schemas
    OUTPUT: generated_query
    """
    print("\n[Node 4] Generating SQL query...")
    
    prompt = f"""
You are a SQL expert. Given the question and schema, write a SQL query to answer it.

Question: {state['user_question']}

Database schema:
{state['table_schemas']}

Rules:
- Write ONLY the SQL query, no explanation
- Use proper SQL syntax for SQLite
- Limit results to 5 rows
- Do NOT include DML statements (INSERT, UPDATE, DELETE)

Return ONLY the SQL query.
"""
    
    response = model.invoke([HumanMessage(content=prompt)])
    response_messages = parse_chat_template_text(response.content)
    query = response_messages[-1]["message"].strip()
    query = query.replace("```sql", "").replace("```", "").strip()

    print(f"  Generated query: {query[:100]}...")
    
    return {
        "generated_query": query
    }


def node_execute_query(state: SQLAgentState, db: SQLDatabase) -> dict:
    """
    Node 5: Execute the generated SQL query against the database.
    
    INPUT: generated_query
    OUTPUT: query_result
    """
    print("\n[Node 5] Executing query...")
    
    try:
        result = db.run(state["generated_query"])
        print(f"  Query executed successfully")
        print(f"  Result preview: {result[:200]}...")
    except Exception as e:
        result = f"ERROR executing query: {str(e)}"
        print(f"  ERROR: {result}")
    
    return {
        "query_result": result
    }


def node_generate_answer(state: SQLAgentState, model) -> dict:
    """
    Node 6: Use LLM to generate a human-readable answer from the query result.
    
    INPUT: user_question, query_result
    OUTPUT: final_answer
    """
    print("\n[Node 6] Generating final answer...")
    
    prompt = f"""
The user asked: "{state['user_question']}"

The SQL query returned these results:
{state['query_result']}

Write a clear, concise answer to the user's question based on these results.
"""
    
    response = model.invoke([HumanMessage(content=prompt)])
    response_messages = parse_chat_template_text(response.content)
    answer = response_messages[-1]["message"].strip()

    print(f"  Answer generated")
    
    return {
        "final_answer": answer
    }


# ============================================================================
# STEP 4: Build the LangGraph
# ============================================================================
def build_agent_graph(model, db, tools):
    """
    Assemble all nodes into a graph.
    
    A graph is like a flow chart:
    - Each box is a node (function)
    - Each arrow is an edge (data flow)
    
    Our graph is linear (no branching):
    START → node_list_tables → node_select_relevant_tables → node_get_schema 
         → node_generate_query → node_execute_query → node_generate_answer → END
    """
    
    # Create a new graph
    graph = StateGraph(SQLAgentState)
    
    # Add nodes (each node is a function + a name)
    # We use lambda to pass db/model since nodes only receive state by default
    graph.add_node("list_tables", lambda state: node_list_tables(state, db))
    graph.add_node("select_tables", lambda state: node_select_relevant_tables(state, model))
    graph.add_node("get_schema", lambda state: node_get_schema(state, db))
    graph.add_node("generate_query", lambda state: node_generate_query(state, model))
    graph.add_node("execute_query", lambda state: node_execute_query(state, db))
    graph.add_node("generate_answer", lambda state: node_generate_answer(state, model))
    
    # Add edges (connections between nodes)
    # This defines the flow: what node runs after what?
    graph.add_edge(START, "list_tables")                    # Start with listing tables
    graph.add_edge("list_tables", "select_tables")          # Then select relevant ones
    graph.add_edge("select_tables", "get_schema")           # Then get their schema
    graph.add_edge("get_schema", "generate_query")          # Then generate SQL
    graph.add_edge("generate_query", "execute_query")       # Then run the SQL
    graph.add_edge("execute_query", "generate_answer")      # Then format the answer
    graph.add_edge("generate_answer", END)                  # Then finish
    
    # Compile the graph into a runnable agent
    return graph.compile()


# ============================================================================
# STEP 5: Run the agent
# ============================================================================
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


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Main entry point."""
    
    print("Initializing SQL Agent...")
    model, db, tools = setup()
    
    print("Building graph...")
    agent = build_agent_graph(model, db, tools)
    
    # Test with a question
    question = "Which genre on average has the longest tracks?"
    result = run_agent(agent, question)
    
    print("\n✓ Agent completed successfully!")


if __name__ == "__main__":
    main()

