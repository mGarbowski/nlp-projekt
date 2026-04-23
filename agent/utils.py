"""Other utilities."""

import re

READ_ONLY_SQL_PREFIXES = (
    "select",
)

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
