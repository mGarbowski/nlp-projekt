def parse_chat_template_text(text: str) -> list[dict[str, str]]:
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
