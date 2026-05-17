import re

from loguru import logger

from agent.chain_of_thought.state import ChainOfThoughtAgentState
from agent.common.llm import LLMAdapter
from agent.common.utils import cleanup_response_with_sql


def node_generate_query_cot(state: ChainOfThoughtAgentState, model: LLMAdapter) -> dict:
    """Use LLM to generate a SQL query based on the question and schema.

    INPUT: user_question, table_schemas
    OUTPUT: generated_query
    """
    logger.info("Generating SQL query with chain-of-thought reasoning")
    if model.uses_visible_cot_prompt:
        prompt = _build_visible_cot_prompt(state)
    else:
        prompt = _build_sql_only_cot_prompt(state)

    query = model.generate_response(prompt)
    reasoning_trace = ""
    if model.uses_visible_cot_prompt:
        think_match = re.search(
            r"<think>(.*?)</think>", query, re.DOTALL | re.IGNORECASE
        )
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


def _build_visible_cot_prompt(state: ChainOfThoughtAgentState) -> str:
    return f"""
    You are a precise SQLite expert for Spider text-to-SQL evaluation.

    Given the question and schema, write a SQL query that best answers the question.

    Question:
    {state["user_question"]}

    Database schema:
    {state["table_schemas"]}

    Output format:
    <think>
    tables: table1, table2
    joins: table1.column = table2.column, or none
    filters: conditions from the question, or none
    aggregation_ordering: group by / having / order by / limit, or none
    output: selected columns or aggregate expressions
    </think>
    SELECT ...

    Rules:
    - Return exactly one <think>...</think> block followed by exactly one SQLite SELECT query.
    - The final SQL must start with SELECT.
    - Do not output the word "think" outside the XML-like tags.
    - Do not output markdown, comments, explanations, or bullet lists outside <think>.
    - Use only tables and columns that explicitly appear in the schema above.
    - Do not invent columns, tables, or join conditions.
    - Before using a column, verify it exists in the corresponding table.
    - If multiple joined tables contain columns with the same name, qualify them with table names or aliases.
    - Use explicit JOIN conditions.
    - If table aliases are needed, use explicit AS, for example: table_name AS T1.
    - Do not use backticks.
    - Do not create aliases for selected columns or aggregate functions.
    - Prefer count(*) for counting rows.
    - If the question asks for entities satisfying both independent conditions, use INTERSECT when appropriate.
    - If aggregation is needed, include the correct GROUP BY clause.
    - If filtering aggregated groups is needed, use HAVING, not WHERE.
    - If the question asks for top/bottom/most/least, use ORDER BY with LIMIT 1.
    - If unsure, prefer a valid query using the schema over an overcomplicated query.
    - Use table aliases only as AS T1, AS T2, AS T3, never bare aliases.
    - For "both", "also", "in both", or two independent aggregate conditions over the same entity, prefer INTERSECT.
    - Do not use CASE WHEN. Prefer INTERSECT, GROUP BY/HAVING, IN, or EXISTS.
    - Never output placeholders such as SELECT ... or generic table names like table1/table2 unless they appear in the schema.
    """


def _build_sql_only_cot_prompt(state: ChainOfThoughtAgentState) -> str:
    return f"""
    You are a precise SQLite text-to-SQL model for Spider evaluation.

    Think internally about the schema and question, but do not output reasoning.
    Return exactly one SQLite SELECT query and nothing else.

    Question:
    {state["user_question"]}

    Database schema:
    {state["table_schemas"]}

    Rules:
    - The response must start with SELECT.
    - Do not output markdown, comments, explanations, bullets, or <think> tags.
    - Do not include any text before or after the SQL query.
    - Use only tables and columns that explicitly appear in the schema above.
    - Do not invent columns, tables, or join conditions.
    - Never output placeholders such as SELECT ...
    - Never use generic table names such as table1, table2, books, authors, or drivers unless they appear exactly in the schema.
    - Before using a column, verify it exists in the corresponding table.
    - If multiple joined tables contain columns with the same name, qualify them with table names or aliases.
    - Use explicit JOIN conditions.
    - If table aliases are needed, use explicit AS, for example: table_name AS T1.
    - Do not use backticks.
    - Do not create aliases for selected columns or aggregate functions.
    - Do not use CASE WHEN. Prefer INTERSECT, GROUP BY/HAVING, IN, or EXISTS.
    - Prefer count(*) for counting rows unless the question asks for distinct values.
    - If the query can be answered from one table, avoid unnecessary joins.
    - If aggregation is needed, include the correct GROUP BY clause.
    - If filtering aggregated groups is needed, use HAVING, not WHERE.
    - If the question asks for top/bottom/most/least, use ORDER BY with LIMIT 1.
    - For oldest/largest/highest/most, use ORDER BY ... DESC LIMIT 1.
    - For youngest/smallest/lowest/least, use ORDER BY ... ASC LIMIT 1.
    - For "both", "also", "in both", or two independent aggregate conditions over the same entity, prefer INTERSECT.
    """
