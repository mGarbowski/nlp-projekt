import json
import os
import re
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import override

from langchain_core.messages import HumanMessage
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace


class LLMModelType(Enum):
    QWEN = "qwen"
    LLAMA = "llama"
    GROQ_QWEN3_32B = "groq-qwen3-32b"
    GROQ_LLAMA_3_1_8B_INSTANT = "groq-llama-3.1-8b-instant"
    GROQ_LLAMA_3_3_70B_VERSATILE = "groq-llama-3.3-70b-versatile"

    @classmethod
    def from_str(cls, model_name: str):
        normalized = model_name.lower()
        for model_type in cls:
            if normalized == model_type.value:
                return model_type

        raise ValueError(f"Unsupported model name: {model_name}")

    @classmethod
    def choices(cls) -> list[str]:
        return [model_type.value for model_type in cls]


class LLMAdapter(ABC):
    uses_visible_cot_prompt = True

    @abstractmethod
    def generate_response(self, prompt: str) -> str: ...


def get_env_value(key: str, aliases: tuple[str, ...] = ()) -> str | None:
    """Read a value from the process environment or a local .env file."""
    if value := os.environ.get(key):
        return value

    keys = (key, *aliases)
    for env_path in iter_env_file_candidates():
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            parsed = parse_env_line(line)
            if not parsed:
                continue
            parsed_key, parsed_value = parsed
            if parsed_key in keys:
                os.environ.setdefault(key, parsed_value)
                return parsed_value

    return None


def iter_env_file_candidates() -> list[Path]:
    """Return .env paths from cwd and parents, with duplicates removed."""
    candidates = [Path.cwd(), *Path.cwd().parents]
    seen = set()
    env_paths = []
    for directory in candidates:
        env_path = directory / ".env"
        if env_path in seen:
            continue
        seen.add(env_path)
        env_paths.append(env_path)
    return env_paths


def parse_env_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    if line.startswith("export "):
        line = line[len("export ") :].strip()

    if "=" not in line:
        return None

    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip().strip("'\"")
    if not key:
        return None

    return key, value


class QwenAdapter(LLMAdapter):
    def __init__(self, temperature: float = 0.3, max_new_tokens: int = 1024):
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.llm = ChatHuggingFace(
            llm=HuggingFacePipeline.from_model_id(
                model_id="Qwen/Qwen2.5-1.5B-Instruct",
                task="text-generation",
                pipeline_kwargs={
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                },
            )
        )

    @override
    def generate_response(self, prompt: str) -> str:
        response = self.llm.invoke([HumanMessage(content=prompt)])
        response_messages = self.parse_chat_template_text(str(response.content))
        return response_messages[-1]["message"].strip()

    @staticmethod
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
                messages.append(
                    {"role": role, "message": "\n".join(current_message_parts)}
                )
                current_message_parts = []
                continue

            current_message_parts.append(line.strip())

        messages.append({"role": role, "message": "\n".join(current_message_parts)})

        return messages


class LlamaAdapter(LLMAdapter):
    def __init__(self, temperature: float = 0.3, max_new_tokens: int = 256):
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.llm = ChatHuggingFace(
            llm=HuggingFacePipeline.from_model_id(
                model_id="meta-llama/Llama-3.2-1B-Instruct",
                task="text-generation",
                pipeline_kwargs={
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                },
            )
        )

    @override
    def generate_response(self, prompt: str) -> str:
        response = self.llm.invoke([HumanMessage(content=prompt)])
        response_text = self.parse_response(str(response.content))
        return response_text.strip()

    @staticmethod
    def parse_response(text: str) -> str:
        """Parse the last response from chat template formatted text"""
        pattern = re.compile(
            r"<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        return re.split(pattern, text)[-1]


class GroqAdapter(LLMAdapter):
    """OpenAI-compatible Groq chat completion adapter."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    uses_visible_cot_prompt = False

    def __init__(
        self,
        model_id: str,
        temperature: float = 0.0,
        max_tokens: int = 384,
        max_retries: int = 5,
        timeout_seconds: int = 120,
        reasoning_format: str | None = None,
        reasoning_effort: str | None = None,
    ):
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.reasoning_format = reasoning_format
        self.reasoning_effort = reasoning_effort
        self.api_key = get_env_value("GROQ_API_KEY", aliases=("groq_api_key",))
        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Put it in .env or export it before using a Groq model."
            )

    @override
    def generate_response(self, prompt: str) -> str:
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Follow the requested output format exactly. "
                        "Do not reveal reasoning. Do not output <think> tags."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.reasoning_format:
            payload["reasoning_format"] = self.reasoning_format
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.API_URL,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "nlp-projekt/0.1 (Python urllib)",
            },
            method="POST",
        )

        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(
                    request, timeout=self.timeout_seconds
                ) as response:
                    response_payload = json.loads(response.read().decode("utf-8"))
                    return self.parse_response(response_payload)
            except urllib.error.HTTPError as error:
                if not self._should_retry(error, attempt):
                    body = error.read().decode("utf-8", errors="replace")
                    raise RuntimeError(
                        f"Groq API request failed with status {error.code}: {body}"
                    ) from error
                self._sleep_before_retry(error, attempt)
            except urllib.error.URLError as error:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Groq API request failed: {error}") from error
                self._sleep_before_retry(None, attempt)

        raise RuntimeError("Groq API request failed after retries.")

    @staticmethod
    def parse_response(payload: dict) -> str:
        return payload["choices"][0]["message"]["content"].strip()

    def _should_retry(self, error: urllib.error.HTTPError, attempt: int) -> bool:
        return attempt < self.max_retries - 1 and (
            error.code == 429 or 500 <= error.code < 600
        )

    @staticmethod
    def _sleep_before_retry(error: urllib.error.HTTPError | None, attempt: int) -> None:
        retry_after = error.headers.get("retry-after") if error else None
        delay = float(retry_after) if retry_after else min(2**attempt, 30)
        time.sleep(delay)


def get_model(model: LLMModelType) -> LLMAdapter:
    match model:
        case LLMModelType.QWEN:
            return QwenAdapter()
        case LLMModelType.LLAMA:
            return LlamaAdapter()
        case LLMModelType.GROQ_QWEN3_32B:
            return GroqAdapter(
                "qwen/qwen3-32b",
                reasoning_format="hidden",
                reasoning_effort="none",
            )
        case LLMModelType.GROQ_LLAMA_3_1_8B_INSTANT:
            return GroqAdapter("llama-3.1-8b-instant")
        case LLMModelType.GROQ_LLAMA_3_3_70B_VERSATILE:
            return GroqAdapter("llama-3.3-70b-versatile")
        case _:
            raise ValueError(f"Unsupported model: {model}")
