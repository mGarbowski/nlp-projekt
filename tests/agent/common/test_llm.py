from pprint import pprint

from agent.common.llm import QwenAdapter, LlamaAdapter


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
