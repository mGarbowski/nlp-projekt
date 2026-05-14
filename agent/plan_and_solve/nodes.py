from langchain_core.language_models import BaseChatModel
from loguru import logger

from agent.plan_and_solve.state import PlanAndSolveAgentState
from agent.utils import get_model_response, cleanup_response_with_sql


def node_generate_query_plan(
    state: PlanAndSolveAgentState, model: BaseChatModel
) -> dict:
    """Create a plan for the query generation.

    Input: user_question, table_schemas
    Output: generate_query_plan
    """
    logger.info("Planning query generation")
    prompt = f"""
        You are a planning assistant for a text-to-SQL system.
        
        Your job is to create a compact execution plan for answering the user's question with a SQL query.
        
        User question:
        {state["user_question"]}
        
        Available table schemas:
        {state["table_schemas"]}
        
        Relevant tables already selected:
        {", ".join(state["relevant_tables"])}
        
        Write a short plan that includes:
        1. The main tables to use
        2. The key columns involved
        3. Any join relationships needed
        4. The filtering, grouping, ordering, or aggregation steps needed
        
        Rules:
        - Use only tables and columns that appear in the schema above.
        - Do not invent columns, tables, or joins.
        - Keep the plan concise and specific.
        - Do not write SQL yet.
        - Do not include any explanation outside the plan.
        - Return only the plan text.
        
        Use this format:
        
        tables: table1, table2, ...
        joins: table1.col = table2.col, ...
        steps:
        - step 1
        - step 2
        - step 3
    """

    plan = get_model_response(model, prompt)

    logger.debug(f"Generated plan {plan[:100]}...")

    return {"generate_query_plan": plan}


def node_generate_query_solve(
    state: PlanAndSolveAgentState, model: BaseChatModel
) -> dict:
    """Generate SQL query using the plan.

    Input: user_question, table_schemas, generate_query_plan
    Output: generated_query
    """

    logger.info("Generating SQL query using the plan")
    prompt = f"""
        You are a SQLite expert.
        
        Your task is to write a single SQL query that answers the user's question using the provided execution plan and schema.
        
        User question:
        {state["user_question"]}
        
        Execution plan:
        {state["generate_query_plan"]}
        
        Available table schemas:
        {state["table_schemas"]}
        
        Rules:
        - Follow the execution plan as closely as possible.
        - Use only tables and columns that appear in the schema above.
        - Do not invent tables, columns, aliases, or join conditions.
        - If the plan mentions a table or column that does not exist in the schema, ignore it and use the closest valid alternative from the schema.
        - Use explicit JOINs when multiple tables are needed.
        - Qualify ambiguous column names with table names or aliases.
        - Return only one valid SQLite SELECT query.
        - Do not include explanations, markdown, comments, or extra text.
        - Do not include DML statements such as INSERT, UPDATE, DELETE, DROP, or ALTER.
        - If aggregation is needed, use valid SQLite syntax and include the correct GROUP BY clause.
        
        Return only the SQL query.
    """
    query = get_model_response(model, prompt)
    query = cleanup_response_with_sql(query)
    logger.debug(f"Generated query preview: {query[:100]}...")

    return {
        "generated_query": query,
    }


# TODO maybe relevant tables need revision
# TODO retry counter
def node_correct_query_plan(
    state: PlanAndSolveAgentState, model: BaseChatModel
) -> dict:
    """Create a plan for the query generation after the last one failed.

    Input: user_question, table_schemas, execution_error, generate_query_plan, generated_query
    Output: generate_query_plan
    """
    logger.info("Correcting query plan")
    prompt = f"""
        You are revising a text-to-SQL execution plan after a failed SQL attempt.
        
        User question:
        {state["user_question"]}
        
        Previous execution plan:
        {state["generate_query_plan"]}
        
        Previous SQL query:
        {state["generated_query"]}
        
        Execution error:
        {state["execution_error"]}
        
        Available table schemas:
        {state["table_schemas"]}
        
        Your job:
        - Update the plan so it avoids the cause of the failure.
        - If the error shows a missing column, wrong join, ambiguous column, or bad table choice, fix the plan accordingly.
        - Keep the plan concise and specific.
        - Use only tables and columns that appear in the schema above.
        - Do not write SQL.
        - Return only the revised plan text.
        
        Use this format:
        
        tables: table1, table2, ...
        joins: table1.col = table2.col, ...
        steps:
        - step 1
        - step 2
        - step 3
    """
    plan = get_model_response(model, prompt)
    logger.debug(f"Corrected plan preview: {plan[:100]}...")
    return {"generate_query_plan": plan}


def node_correct_query_solve(
    state: PlanAndSolveAgentState, model: BaseChatModel
) -> dict:
    """Generate SQL query using the plan after the last one failed.

    Input: user_question, table_schemas, execution_error, generate_query_plan, generated_query
    Output: generated_query
    """
    logger.info("Correcting SQL query using revised plan")
    prompt = f"""
        You are a SQLite expert fixing a failed query.
        
        User question:
        {state["user_question"]}
        
        Revised execution plan:
        {state["generate_query_plan"]}
        
        Previous SQL query:
        {state["generated_query"]}
        
        Execution error:
        {state["execution_error"]}
        
        Available table schemas:
        {state["table_schemas"]}
        
        Rules:
        - Use the revised plan as the main guide.
        - You may rewrite the query completely if needed.
        - Use only tables and columns that appear in the schema above.
        - Do not invent tables, columns, aliases, or join conditions.
        - Use explicit JOINs when multiple tables are needed.
        - Qualify ambiguous column names with table names or aliases.
        - Return only one valid SQLite SELECT query.
        - Do not include explanations, markdown, comments, or extra text.
        - Do not include DML statements such as INSERT, UPDATE, DELETE, DROP, or ALTER.
        - If aggregation is needed, include the correct GROUP BY clause.
        
        Return only the SQL query.
    """
    query = get_model_response(model, prompt)
    query = cleanup_response_with_sql(query)
    logger.debug(f"Corrected query preview: {query[:100]}...")
    return {"generated_query": query}
