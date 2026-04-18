"""Nodes for the agent's graph."""

from loguru import logger
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage

from .state import AgentState
from .utils import parse_chat_template_text


def node_list_tables(state: AgentState, db: SQLDatabase) -> dict:
    """
    Node 1: List all available tables.

    INPUT: user_question
    OUTPUT: all_tables
    """
    logger.info("[Node 1] Listing all tables")
    tables = db.get_usable_table_names()
    logger.info(f"Found tables: {tables}")

    return {"all_tables": tables}


def node_select_relevant_tables(state: AgentState, model) -> dict:
    """
    Node 2: Use LLM to select which tables are relevant to the question.

    INPUT: user_question, all_tables
    OUTPUT: relevant_tables
    """
    logger.info("[Node 2] Selecting relevant tables")

    prompt = f"""
Given this question: "{state["user_question"]}"

These tables are available: {", ".join(state["all_tables"])}

Which tables would you need to query to answer the question?
Return ONLY a comma-separated list of table names, nothing else.
Example: "Artist,Album,Genre"
"""

    response = model.invoke([HumanMessage(content=prompt)])
    response_messages = parse_chat_template_text(response.content)
    table_names = response_messages[-1]["message"].split(",")
    table_names = [t.strip() for t in table_names]

    logger.info(f"Selected tables: {table_names}")

    return {"relevant_tables": table_names}


def node_get_schema(state: AgentState, db: SQLDatabase) -> dict:
    """
    Node 3: Fetch the schema (column names, types) for relevant tables.

    INPUT: relevant_tables
    OUTPUT: table_schemas
    """
    logger.info("[Node 3] Getting table schemas")

    schemas = []
    for table_name in state["relevant_tables"]:
        try:
            schema = db.get_table_info([table_name])
            schemas.append(schema)
        except Exception as e:
            logger.warning(f"Could not get schema for {table_name}: {e}")

    schema_text = "\n\n".join(schemas)
    logger.info(f"Schema retrieved for tables: {state['relevant_tables']}")

    return {"table_schemas": schema_text}


def node_generate_query(state: AgentState, model) -> dict:
    """
    Node 4: Use LLM to generate a SQL query based on the question and schema.

    INPUT: user_question, table_schemas
    OUTPUT: generated_query
    """
    logger.info("[Node 4] Generating SQL query")

    prompt = f"""
You are a SQL expert. Given the question and schema, write a SQL query to answer it.

Question: {state["user_question"]}

Database schema:
{state["table_schemas"]}

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

    logger.debug(f"Generated query preview: {query[:100]}...")

    return {"generated_query": query}


def node_execute_query(state: AgentState, db: SQLDatabase) -> dict:
    """
    Node 5: Execute the generated SQL query against the database.

    INPUT: generated_query
    OUTPUT: query_result
    """
    logger.info("[Node 5] Executing query")

    try:
        result = str(db.run(state["generated_query"]))
        logger.info("Query executed successfully")
        logger.debug(f"Result preview: {result[:200]}...")
    except Exception as e:
        result = f"ERROR executing query: {str(e)}"
        logger.exception(
            f"{result}",
        )

    return {"query_result": result}


def node_generate_answer(state: AgentState, model) -> dict:
    """
    Node 6: Use LLM to generate a human-readable answer from the query result.

    INPUT: user_question, query_result
    OUTPUT: final_answer
    """
    logger.info("[Node 6] Generating final answer")

    prompt = f"""
The user asked: "{state["user_question"]}"

The SQL query returned these results:
{state["query_result"]}

Write a clear, concise answer to the user's question based on these results.
"""

    response = model.invoke([HumanMessage(content=prompt)])
    response_messages = parse_chat_template_text(response.content)
    answer = response_messages[-1]["message"].strip()

    logger.info("Answer generated")

    return {"final_answer": answer}
