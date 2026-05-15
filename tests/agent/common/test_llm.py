from pprint import pprint

from agent.common.llm import QwenAdapter


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
