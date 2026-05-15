from abc import ABC, abstractmethod
from enum import Enum
from typing import override

from langchain_core.messages import HumanMessage
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace


class LLMModelType(Enum):
    QWEN = "qwen"
    LLAMA = "llama"

    @classmethod
    def from_str(cls, model_name: str):
        match model_name.lower():
            case "qwen":
                return cls.QWEN
            case "llama":
                return cls.LLAMA
            case _:
                raise ValueError(f"Unsupported model name: {model_name}")


class LLMAdapter(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str: ...


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


def get_model(model: LLMModelType) -> LLMAdapter:
    match model:
        case LLMModelType.QWEN:
            return QwenAdapter()
        case LLMModelType.LLAMA:
            raise NotImplementedError("LLaMA model wrapper not implemented yet.")
        case _:
            raise ValueError(f"Unsupported model: {model}")
