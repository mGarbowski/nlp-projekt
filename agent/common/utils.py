"""Other utilities."""

import re

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

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


def parse_chat_template_text(text: str) -> list[dict[str, str]]:
    """Parse Qwen chat template generated text into a list of messages."""
    messages = []
    lines = text.strip().splitlines()
    role = None
    current_message_parts = []
    for line in lines:
        if "<|im_start|>" in line:
            role = line.split("<|im_start|>")[1]
            current_message_parts = []
            continue

        if "<|im_end|>" in line:
            current_message_parts.append(line.replace("<|im_end|>", "").strip())
            messages.append({"role": role, "message": "\n".join(current_message_parts)})
            current_message_parts = []
            continue

        current_message_parts.append(line.strip())

    messages.append({"role": role, "message": "\n".join(current_message_parts)})

    return messages


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


def get_model_response(model: BaseChatModel, prompt: str) -> str:
    """Generate and parse the LLM response.

    Uses the Qwen chat template parser.
    """
    response = model.invoke([HumanMessage(content=prompt)])
    response_messages = parse_chat_template_text(response.content)
    return response_messages[-1]["message"].strip()


def cleanup_response_with_sql(query: str) -> str:
    """Cleanup common LLM artifacts"""
    query = query.replace("```sql", "").replace("```", "").strip()
    query = query.split("Explanation:")[0].strip()

    if ";" in query:
        query = query.split(";")[0].strip() + ";"

    return query
