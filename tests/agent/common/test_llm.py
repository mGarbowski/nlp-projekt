from pprint import pprint

from agent.common.llm import (
    QwenAdapter,
    LlamaAdapter,
    LLMModelType,
    GroqAdapter,
    get_env_value,
    parse_env_line,
)


def test_parse_chat_text():
    example = """<|im_start|>system
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>
<|im_start|>user
Given this question: "Which genre on average has the longest tracks?"...
Example: "Artist,Album,Genre"
<|im_end|>
<|im_start|>assistant
Track,Genre"""

    expected = [
        {
            "role": "system",
            "message": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
        },
        {
            "role": "user",
            "message": 'Given this question: "Which genre on average has the longest tracks?"...\nExample: "Artist,Album,Genre"\n',
        },
        {"role": "assistant", "message": "Track,Genre"},
    ]

    actual = QwenAdapter.parse_chat_template_text(example)
    pprint(actual)
    assert actual == expected


def test_parse_llama():
    example = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Cutting Knowledge Date: December 2023
Today Date: 15 May 2026

<|eot_id|><|start_header_id|>user<|end_header_id|>

You are a helpful SQL assistant.
        
        To answer the question: "How many singers do we have?"
        
        Which tables from those will be needed to answer?: concert, singer, singer_in_concert, stadium
        
        Return ONLY a comma-separated list of table names that are relevant to answering the question, nothing else.
        Example: 
            question: "How many albums does each artist have?"
            all tables: Artist,Album,Genre
            answer: Artist,Album<|eot_id|><|start_header_id|>assistant<|end_header_id|>

To answer the question "How many singers do we have?", we need the following tables:

- Singer
- Singer_in_concert
- Stadium"""
    expected = """To answer the question "How many singers do we have?", we need the following tables:

- Singer
- Singer_in_concert
- Stadium"""
    assert LlamaAdapter.parse_response(example) == expected


def test_model_type_parses_groq_models():
    assert LLMModelType.from_str("groq-qwen3-32b") == LLMModelType.GROQ_QWEN3_32B
    assert (
        LLMModelType.from_str("groq-llama-3.1-8b-instant")
        == LLMModelType.GROQ_LLAMA_3_1_8B_INSTANT
    )
    assert (
        LLMModelType.from_str("groq-llama-3.3-70b-versatile")
        == LLMModelType.GROQ_LLAMA_3_3_70B_VERSATILE
    )


def test_groq_parse_response():
    payload = {
        "choices": [
            {
                "message": {
                    "content": "SELECT COUNT(*) FROM singer;",
                }
            }
        ]
    }

    assert GroqAdapter.parse_response(payload) == "SELECT COUNT(*) FROM singer;"


def test_groq_uses_sql_only_cot_prompt():
    assert QwenAdapter.uses_visible_cot_prompt
    assert LlamaAdapter.uses_visible_cot_prompt
    assert not GroqAdapter.uses_visible_cot_prompt


def test_parse_env_line():
    assert parse_env_line("GROQ_API_KEY=abc123") == ("GROQ_API_KEY", "abc123")
    assert parse_env_line("export GROQ_API_KEY='abc123'") == (
        "GROQ_API_KEY",
        "abc123",
    )
    assert parse_env_line("# ignored") is None


def test_get_env_value_reads_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    (tmp_path / ".env").write_text("GROQ_API_KEY=test-key\n", encoding="utf-8")

    assert get_env_value("GROQ_API_KEY") == "test-key"
