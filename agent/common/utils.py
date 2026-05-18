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

SQL_CLAUSE_KEYWORDS = {
    "where",
    "join",
    "inner",
    "left",
    "right",
    "full",
    "cross",
    "on",
    "group",
    "order",
    "having",
    "limit",
    "intersect",
    "union",
    "except",
}


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
    """Cleanup common LLM artifacts and normalize SQL for Spider evaluation."""
    query = query.replace("```sql", "").replace("```", "").strip()
    query = re.sub(r"</?sql>", "", query, flags=re.IGNORECASE).strip()
    query = re.sub(r"</?query>", "", query, flags=re.IGNORECASE).strip()
    query = _remove_visible_reasoning(query)
    query = _trim_to_sql_marker(query)
    query = _extract_sql_select_statement(query)

    if ";" in query:
        query = query.split(";")[0].strip() + ";"
    else:
        query = re.split(
            r"\n\s*(?:explanation|thought|observation|answer|final answer)\s*:",
            query,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()
        query = re.split(
            r"(?i)\.\s+(?:wait|for the|then|second|first|the|that|but|so|because|let|i|no)\b",
            query,
            maxsplit=1,
        )[0].strip()

    return normalize_sql_for_spider(query)


def normalize_sql_for_spider(query: str) -> str:
    """Normalize generated SQL to reduce Spider parser failures.

    The Spider evaluator is stricter than SQLite in a few places, especially
    around aliases. This function preserves SQL meaning where possible while
    avoiding common parser failures caused by model formatting artifacts.
    """
    query = query.strip().replace("`", "")
    if not query:
        return query

    query = _normalize_table_aliases(query)
    query = _remove_select_output_aliases(query)
    query = re.sub(r"\s+", " ", query).strip()

    if ";" in query:
        query = query.split(";", 1)[0].strip() + ";"

    return query


def cleanup_table_names_response(response_text: str) -> str:
    response_text = response_text.strip()
    response_text = response_text.replace("`", "")
    response_text = response_text.replace("'", "")
    response_text = response_text.replace('"', "")
    return response_text


def _remove_visible_reasoning(text: str) -> str:
    think_end = text.lower().rfind("</think>")
    if think_end >= 0:
        return text[think_end + len("</think>") :].strip()

    return re.sub(r"(?is)<think>.*?</think>", " ", text).strip()


def _trim_to_sql_marker(text: str) -> str:
    markers = [
        "the sql query would be:",
        "the sql would be:",
        "main query would be:",
        "query would be:",
        "final sql:",
        "sql query:",
        "sql:",
        "answer:",
    ]
    lower = text.lower()
    positions = [(lower.rfind(marker), marker) for marker in markers]
    position, marker = max(positions, key=lambda item: item[0])
    if position >= 0:
        return text[position + len(marker) :].strip()

    return text


def _extract_sql_select_statement(text: str) -> str:
    select_matches = list(re.finditer(r"\bselect\b", text, flags=re.IGNORECASE))
    for match in select_matches:
        candidate = text[match.start() :].strip()
        if _looks_like_sql_select(candidate):
            return candidate

    return text


def _looks_like_sql_select(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    if not normalized.startswith("select "):
        return False
    if re.match(
        r"select\s+(?:the|a|an|those|these|all the|from|what|which)\b",
        normalized,
    ):
        return False

    return bool(re.search(r"\bfrom\b", normalized))


def extract_valid_table_names(response_text: str, valid_tables: list[str]) -> list[str]:
    """Extract valid table names from a model response.

    Prefer the tail of the response after phrases such as "relevant tables" so
    explanatory answers that mention every table do not force an all-table
    fallback.
    """
    response_text = cleanup_table_names_response(response_text)
    candidates = _candidate_table_response_text(response_text)
    selected = _extract_tables_from_text(candidates, valid_tables)
    if selected:
        return selected

    return _extract_tables_from_text(response_text, valid_tables)


def _candidate_table_response_text(response_text: str) -> str:
    lower = response_text.lower()
    markers = [
        "relevant tables",
        "tables are",
        "answer:",
        "answer is",
        "return:",
    ]
    positions = [lower.rfind(marker) for marker in markers]
    best = max(positions)
    if best >= 0:
        return response_text[best:]
    return response_text


def _extract_tables_from_text(text: str, valid_tables: list[str]) -> list[str]:
    selected = []
    for table_name in valid_tables:
        pattern = r"(?<![A-Za-z0-9_])" + re.escape(table_name) + r"(?![A-Za-z0-9_])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            selected.append(table_name)
    return selected


def _normalize_table_aliases(query: str) -> str:
    def replace_alias(match: re.Match) -> str:
        clause = match.group(1)
        table_name = match.group(2)
        alias = match.group(3)
        if alias.lower() in SQL_CLAUSE_KEYWORDS:
            return match.group(0)
        return f"{clause} {table_name} AS {alias}"

    return re.sub(
        r"\b(from|join)\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?!as\b)([A-Za-z_][A-Za-z0-9_]*)\b",
        replace_alias,
        query,
        flags=re.IGNORECASE,
    )


def _remove_select_output_aliases(query: str) -> str:
    from_match = re.search(r"\bfrom\b", query, flags=re.IGNORECASE)
    if not from_match:
        cleaned_query, _ = _strip_alias_from_select_items(query)
        return cleaned_query

    select_part = query[: from_match.start()]
    rest = query[from_match.start() :]
    cleaned_select, aliases = _strip_alias_from_select_items(select_part)
    for alias, expression in aliases.items():
        rest = re.sub(
            rf"(?i)(\border\s+by\s+){re.escape(alias)}(\b)",
            lambda match: f"{match.group(1)}{expression}{match.group(2)}",
            rest,
        )
        rest = re.sub(
            rf"(?i)(\bgroup\s+by\s+){re.escape(alias)}(\b)",
            lambda match: f"{match.group(1)}{expression}{match.group(2)}",
            rest,
        )
        rest = re.sub(
            rf"(?i)(\bhaving\s+){re.escape(alias)}(\b)",
            lambda match: f"{match.group(1)}{expression}{match.group(2)}",
            rest,
        )
        rest = re.sub(
            rf"(?i)(,\s*){re.escape(alias)}(\b)",
            lambda match: f"{match.group(1)}{expression}{match.group(2)}",
            rest,
        )
    return f"{cleaned_select} {rest.lstrip()}"


def _strip_alias_from_select_items(select_part: str) -> tuple[str, dict[str, str]]:
    aliases = {}
    prefix_match = re.match(r"(?is)(\s*select\s+)(.*)", select_part)
    if not prefix_match:
        return select_part, aliases

    prefix = prefix_match.group(1)
    select_body = prefix_match.group(2)
    items = _split_top_level_commas(select_body)
    cleaned_items = []
    for item in items:
        cleaned_item, alias = _strip_single_select_alias(item)
        if alias:
            aliases[alias.lower()] = cleaned_item.strip()
        cleaned_items.append(cleaned_item)

    return prefix + ", ".join(cleaned_items), aliases


def _strip_single_select_alias(item: str) -> tuple[str, str | None]:
    match = re.search(
        r"(?is)\s+as\s+([A-Za-z_][A-Za-z0-9_]*(?:\s+[A-Za-z_][A-Za-z0-9_]*)*|\"[^\"]+\"|'[^']+')\s*$",
        item,
    )
    if not match:
        return item.strip(), None

    alias = match.group(1).strip("\"'")
    return item[: match.start()].strip(), alias


def _split_top_level_commas(text: str) -> list[str]:
    parts = []
    start = 0
    depth = 0
    quote = None
    for idx, char in enumerate(text):
        if quote:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            parts.append(text[start:idx].strip())
            start = idx + 1
    parts.append(text[start:].strip())
    return parts
