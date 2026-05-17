"""Other utilities."""

import re


READ_ONLY_SQL_PREFIXES = ("select",)

FORBIDDEN_SQL_KEYWORDS = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "attach",
    "detach",
    "pragma",
)


def is_read_only_sql(query: str) -> bool:
    """Return True for read-only queries allowed in Spider-style evaluation."""
    normalized = query.strip().lower().lstrip("(")
    if not normalized:
        return False

    if not normalized.startswith(READ_ONLY_SQL_PREFIXES):
        return False

    # Avoid obvious write operations anywhere in the query text.
    pattern = r"\b(" + "|".join(FORBIDDEN_SQL_KEYWORDS) + r")\b"
    return re.search(pattern, normalized) is None


def cleanup_response_with_sql(query: str) -> str:
    """Cleanup common LLM artifacts"""
    query = query.replace("```sql", "").replace("```", "").strip()
    query = query.split("Explanation:")[0].strip()

    if ";" in query:
        query = query.split(";")[0].strip() + ";"

    return query


def cleanup_table_names_response(response_text: str) -> str:
    response_text = response_text.strip()
    response_text = response_text.replace("`", "")
    response_text = response_text.replace("'", "")
    response_text = response_text.replace('"', "")
    return response_text
