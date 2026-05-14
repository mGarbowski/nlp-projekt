"""Common nodes for the agent's graph."""

from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from loguru import logger

from agent.common.state import BaseAgentState
from agent.common.utils import (
    get_model_response,
    cleanup_response_with_sql,
    is_read_only_sql,
)


def node_list_tables(state: BaseAgentState, db: SQLDatabase) -> dict:
    """List all available tables.

    INPUT: user_question
    OUTPUT: all_tables
    """
    logger.info("Listing all tables")
    tables = db.get_usable_table_names()
    logger.info(f"Found tables: {tables}")

    return {"all_tables": tables}


def node_select_relevant_tables(state: BaseAgentState, model) -> dict:
    """Use LLM to select which tables are relevant to the question.

    INPUT: user_question, all_tables
    OUTPUT: relevant_tables
    """
    logger.info("Selecting relevant tables")

    prompt = f"""
        Given this question: "{state["user_question"]}"
        
        These tables are available: {", ".join(state["all_tables"])}
        
        Which tables would you need to query to answer the question?
        Return ONLY a comma-separated list of table names, nothing else.
        Example: "Artist,Album,Genre"
    """

    table_names = get_model_response(model, prompt).split(",")
    table_names = [t.strip() for t in table_names]

    valid_tables = set(state["all_tables"])
    selected_tables = [table for table in table_names if table in valid_tables]
    if not selected_tables:
        logger.warning(
            "Model did not return valid table names. Falling back to all tables."
        )
        selected_tables = list(state["all_tables"])

    logger.debug(f"Selected tables: {selected_tables}")

    return {"relevant_tables": selected_tables}


def node_get_schema(state: BaseAgentState, db: SQLDatabase) -> dict:
    """Fetch the schema (column names, types) for relevant tables.

    INPUT: relevant_tables
    OUTPUT: table_schemas
    """
    logger.info("Getting table schemas")

    schemas = []
    for table_name in state["relevant_tables"]:
        try:
            schema = db.get_table_info([table_name])
            schemas.append(schema)
        except Exception as e:
            logger.warning(f"Could not get schema for {table_name}: {e}")

    schema_text = "\n\n".join(schemas)
    logger.debug(f"Schema retrieved for tables: {state['relevant_tables']}")

    return {"table_schemas": schema_text}


def node_generate_query_base(state: BaseAgentState, model: BaseChatModel) -> dict:
    """Use LLM to generate a SQL query based on the question and schema.

    INPUT: user_question, table_schemas
    OUTPUT: generated_query
    """
    logger.info("Generating SQL query")
    prompt = f"""
        You are a precise SQLite expert for text-to-SQL evaluation.
        
        Given the question and schema, write a SQL query that best answers the question.
        
        Question: {state["user_question"]}
        
        Database schema:
        {state["table_schemas"]}
        
        Rules:
        - Use ONLY tables and columns that explicitly appear in the schema above.
        - Do NOT invent columns.
        - Before using a column, make sure it exists in the corresponding table.
        - If multiple joined tables contain columns with the same name, ALWAYS qualify them with table names or aliases.
        - Use explicit JOIN conditions.
        - Do NOT use a column from a table unless that column is shown in the schema for that table.
        - If the question can be answered from one table, avoid unnecessary joins.
        - Return ONLY one valid SQLite SELECT query.
        - Do NOT add explanations, markdown, or comments.
    """
    query = get_model_response(model, prompt)
    query = cleanup_response_with_sql(query)
    logger.debug(f"Generated query preview: {query[:100]}...")
    return {"generated_query": query}


def node_execute_query(state: BaseAgentState, db: SQLDatabase) -> dict:
    """Execute the generated SQL query against the database.

    INPUT: generated_query
    OUTPUT: query_result, execution_error
    """
    logger.info("Executing query")

    query = state["generated_query"].strip()
    if not is_read_only_sql(query):
        error = "Only read-only SELECT queries are allowed. The generated query appears to be non-read-only or invalid."
        logger.warning(error)
        return {"query_result": "", "execution_error": error}

    try:
        result = str(db.run(query))
        logger.info("Query executed successfully")
        logger.debug(f"Result preview: {result[:200]}...")
        return {"query_result": result, "execution_error": ""}
    except Exception as e:
        error = str(e)
        logger.error(f"ERROR executing query: {error}")
        return {"query_result": "", "execution_error": error}


def node_use_all_tables(state: BaseAgentState) -> dict:
    logger.info("Falling back to all tables after schema-linking failure")
    return {
        "relevant_tables": list(state["all_tables"]),
        "table_schemas": "",
        "generated_query": "",
        "used_all_tables_fallback": True,
    }


def should_retry_after_execution(state: BaseAgentState) -> str:
    error = state["execution_error"].lower().strip()

    if not error:
        return "done"

    if ("no such column" in error or "no such table" in error) and not state[
        "used_all_tables_fallback"
    ]:
        return "use_all_tables"

    if state["correction_attempts"] < state["max_correction_attempts"]:
        return "correct_query"

    logger.warning("Max correction attempts reached; returning last generated query.")
    return "done"


def node_correct_query(state: BaseAgentState, model) -> dict:
    """Try to repair SQL after validation or execution failure."""
    next_attempt = state["correction_attempts"] + 1
    logger.info(
        f"Correcting SQL after failure (attempt {next_attempt}/{state['max_correction_attempts']})"
    )

    prompt = f"""
        You are fixing a SQLite query for a text-to-SQL task.
        Return ONLY a corrected SQL query.
        
        Question:
        {state["user_question"]}
        
        Database schema:
        {state["table_schemas"]}
        
        Previous SQL:
        {state["generated_query"]}
        
        Execution/validation error:
        {state["execution_error"]}
        
        Rules:
        - Return ONLY one corrected SQLite SELECT query.
        - Fix the query using the error message and the schema.
        - Do NOT reuse any column name that appears in the error unless you verify it exists in the schema.
        - If the error says "no such column", replace that column with an existing one from the schema or rewrite the query.
        - If the error says "ambiguous column name", fully qualify that column with a table name or alias everywhere it appears.
        - If the query uses an unnecessary join, remove it.
        - Use ONLY tables and columns explicitly present in the schema.
        - Do NOT invent aliases or table names.
    """
    query = get_model_response(model, prompt)
    query = cleanup_response_with_sql(query)

    logger.debug(f"Corrected query preview: {query[:100]}...")

    return {
        "generated_query": query,
        "correction_attempts": next_attempt,
    }


def node_generate_answer(state: BaseAgentState, model) -> dict:
    """Use LLM to generate a human-readable answer from the query result.

    INPUT: user_question, query_result
    OUTPUT: final_answer
    """
    logger.info("Generating final answer")

    prompt = f"""
        The user asked: "{state["user_question"]}"
        
        The SQL query returned these results:
        {state["query_result"]}
        
        Write a clear, concise answer to the user's question based on these results.
    """
    answer = get_model_response(model, prompt)

    logger.info("Answer generated")

    return {"final_answer": answer}
