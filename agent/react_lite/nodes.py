"""Nodes for the ReAct-lite SQL agent strategy."""

import re

from loguru import logger

from agent.common.llm import LLMAdapter
from agent.common.utils import cleanup_response_with_sql
from agent.react_lite.state import ReactLiteAgentState, ReactLiteHistoryEntry


def _format_react_history(history: list[ReactLiteHistoryEntry]) -> str:
    if not history:
        return "No previous actions."

    formatted_entries = []
    for idx, entry in enumerate(history, start=1):
        formatted_entries.append(
            "\n".join(
                [
                    f"Attempt {idx}:",
                    f"Thought: {entry['thought'] or 'not shown'}",
                    f"Action SQL: {entry['action']}",
                    f"Observation: {entry['observation']}",
                ]
            )
        )

    return "\n\n".join(formatted_entries)


def _parse_react_response(response: str) -> tuple[str, str]:
    """Extract Thought and SQL action from a ReAct-style model response."""
    match = re.search(
        r"(?:thought|revision)\s*:\s*(.*?)\s*(?:action\s+sql|sql|action)\s*:\s*(.*)",
        response,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        thought = match.group(1).strip()
        query = match.group(2).strip()
    else:
        logger.warning("Model did not follow Thought/SQL format.")
        thought = ""
        query = response.strip()

    query = re.split(
        r"\n\s*(?:observation|final answer|answer)\s*:",
        query,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    query = cleanup_response_with_sql(query)

    return thought, query


def node_generate_react_action(state: ReactLiteAgentState, model: LLMAdapter) -> dict:
    """Generate the next Thought and SQL action from the current observation history.

    Input: user_question, table_schemas, react_history
    Output: current_thought, generated_query
    """
    attempt_no = len(state["react_history"]) + 1
    logger.info(f"Generating ReAct-lite SQL action (attempt {attempt_no})")

    if model.uses_visible_cot_prompt:
        prompt = _build_visible_react_prompt(state)
    else:
        prompt = _build_sql_only_react_prompt(state)

    response = model.generate_response(prompt)
    thought, query = _parse_react_response(response)

    logger.debug(f"ReAct-lite thought preview: {thought[:120]}...")
    logger.debug(f"ReAct-lite query preview: {query[:120]}...")

    return {
        "current_thought": thought,
        "generated_query": query,
    }


def _build_visible_react_prompt(state: ReactLiteAgentState) -> str:
    return f"""
        You are a ReAct-lite text-to-SQL agent for SQLite.

        The loop is:
        Thought: reason about the question, schema, and previous observations.
        Action: produce one SQL SELECT query.
        Observation: the database returns either a result or an execution error.

        Your goal is to answer the user question with a valid SQL query.

        User question:
        {state["user_question"]}

        Relevant tables:
        {", ".join(state["relevant_tables"])}

        Available table schemas:
        {state["table_schemas"]}

        Previous Thought/Action/Observation history:
        {_format_react_history(state["react_history"])}

        Rules:
        - Use the history to revise the reasoning path, not only to patch the previous SQL text.
        - If a previous observation contains an error, explain what assumption caused it.
        - If there is no previous history, reason from the question and schema.
        - Use ONLY tables and columns that explicitly appear in the schema above.
        - Do NOT invent tables, columns, aliases, or join conditions.
        - Before using a column, verify it exists in the corresponding table.
        - Use explicit JOIN conditions when multiple tables are needed.
        - If multiple joined tables contain columns with the same name, qualify them.
        - If table aliases are needed, use explicit AS, for example: table_name AS T1.
        - Do not use backticks.
        - Do not create aliases for selected columns or aggregate functions.
        - Prefer count(*) for counting rows unless the question asks for distinct values.
        - If the query can be answered from one table, avoid unnecessary joins.
        - If aggregation is needed, include the correct GROUP BY clause.
        - If filtering aggregated groups is needed, use HAVING, not WHERE.
        - If the question asks for top/bottom/most/least, use ORDER BY with LIMIT 1.
        - For oldest/largest/highest/most, use ORDER BY ... DESC LIMIT 1.
        - For youngest/smallest/lowest/least, use ORDER BY ... ASC LIMIT 1.
        - For "both", "also", "in both", or two independent aggregate conditions over the same entity, prefer INTERSECT.
        - Do not use CASE WHEN. Prefer INTERSECT, GROUP BY/HAVING, IN, or EXISTS.
        - Never output placeholders such as SELECT ... or generic table names like table1/table2 unless they appear in the schema.
        - Return one valid SQLite SELECT query as the action.
        - Do not include markdown, comments, or extra explanation.
        - Do not include DML statements such as INSERT, UPDATE, DELETE, DROP, or ALTER.

        Return exactly this format:
        Thought: <short diagnosis or reasoning for this attempt>
        SQL: <one SQLite SELECT query>
    """


def _build_sql_only_react_prompt(state: ReactLiteAgentState) -> str:
    return f"""
        You are a precise ReAct-lite SQLite text-to-SQL model for Spider evaluation.

        Think internally about the question, schema, and previous observations, but do not output reasoning.
        Use the previous actions and observations to revise the SQL when an earlier attempt failed.
        Return exactly one SQLite SELECT query and nothing else.

        User question:
        {state["user_question"]}

        Relevant tables:
        {", ".join(state["relevant_tables"])}

        Available table schemas:
        {state["table_schemas"]}

        Previous SQL actions and database observations:
        {_format_react_history(state["react_history"])}

        Rules:
        - The response must start with SELECT.
        - Do not output markdown, comments, explanations, bullets, Thought, Revision, Observation, or <think> tags.
        - Do not include any text before or after the SQL query.
        - Use only tables and columns that explicitly appear in the schema above.
        - Do not invent columns, tables, aliases, or join conditions.
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


def node_record_react_observation(state: ReactLiteAgentState) -> dict:
    """Record the database observation for the last SQL action."""
    if state["execution_error"]:
        observation = f"ERROR: {state['execution_error']}"
        correction_attempts = state["correction_attempts"] + 1
    else:
        result_preview = state["query_result"][:500]
        observation = f"RESULT: {result_preview}"
        correction_attempts = state["correction_attempts"]

    history_entry: ReactLiteHistoryEntry = {
        "thought": state["current_thought"],
        "action": state["generated_query"],
        "observation": observation,
    }
    history = [*state["react_history"], history_entry]

    logger.debug(f"Recorded ReAct-lite observation: {observation[:160]}...")

    return {
        "react_history": history,
        "correction_attempts": correction_attempts,
    }


def should_continue_react(state: ReactLiteAgentState) -> str:
    """Route ReAct-lite after recording the last observation."""
    error = state["execution_error"].lower().strip()

    if not error:
        return "done"

    if state["correction_attempts"] > state["max_correction_attempts"]:
        logger.warning("Max ReAct-lite correction attempts reached.")
        return "done"

    if ("no such column" in error or "no such table" in error) and not state[
        "used_all_tables_fallback"
    ]:
        return "use_all_tables"

    return "retry"
