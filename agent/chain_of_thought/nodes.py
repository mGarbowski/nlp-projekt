import re

from langchain_core.language_models import BaseChatModel
from loguru import logger

from agent.chain_of_thought.state import ChainOfThoughtAgentState
from agent.common.utils import get_model_response, cleanup_response_with_sql


def node_generate_query_cot(
    state: ChainOfThoughtAgentState, model: BaseChatModel
) -> dict:
    """Use LLM to generate a SQL query based on the question and schema.

    INPUT: user_question, table_schemas
    OUTPUT: generated_query
    """
    logger.info("Generating SQL query with chain-of-thought reasoning")
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
        - First write a compact SQL plan inside <think>...</think>.
        - The plan must contain at most 4 short lines:
          1. relevant tables
          2. join keys, if needed
          3. filters/grouping/ordering/aggregation, if needed
          4. selected output columns
        - Use only table and column names that appear in the schema.
        - If unsure, prefer a simpler query using fewer joins.
        - After </think>, output exactly one valid SQLite SELECT query and nothing else.
        - Do not output markdown, comments, or explanation outside <think>.
    """
    query = get_model_response(model, prompt)
    reasoning_trace = ""
    think_match = re.search(r"<think>(.*?)</think>", query, re.DOTALL | re.IGNORECASE)
    if think_match:
        reasoning_trace = think_match.group(1).strip()
        query = query.replace(think_match.group(0), "").strip()
    else:
        logger.warning("Model failed to use <think> tags for reasoning.")

    query = cleanup_response_with_sql(query)

    logger.debug(f"Generated query preview: {query[:100]}...")
    return {
        "generated_query": query,
        "reasoning_trace": reasoning_trace,
    }
