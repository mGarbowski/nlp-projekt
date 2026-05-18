from agent.common.llm import LLMAdapter
from agent.react_lite.nodes import node_generate_react_action


class FakeModel(LLMAdapter):
    def __init__(self, uses_visible_cot_prompt: bool, response: str):
        self.uses_visible_cot_prompt = uses_visible_cot_prompt
        self.response = response
        self.prompt = ""

    def generate_response(self, prompt: str) -> str:
        self.prompt = prompt
        return self.response


def make_state():
    return {
        "user_question": "How many singers are there?",
        "relevant_tables": ["singer"],
        "table_schemas": "CREATE TABLE singer (Singer_ID INTEGER, Name TEXT);",
        "react_history": [],
    }


def test_react_lite_uses_visible_prompt_for_local_models():
    model = FakeModel(
        uses_visible_cot_prompt=True,
        response="Thought: Count rows in singer.\nSQL: SELECT count(*) FROM singer;",
    )

    result = node_generate_react_action(make_state(), model)

    assert "Return exactly this format:" in model.prompt
    assert "Thought:" in model.prompt
    assert result["current_thought"] == "Count rows in singer."
    assert result["generated_query"] == "SELECT count(*) FROM singer;"


def test_react_lite_uses_sql_only_prompt_for_groq_models():
    model = FakeModel(
        uses_visible_cot_prompt=False,
        response="SELECT count(*) FROM singer;",
    )

    result = node_generate_react_action(make_state(), model)

    assert "Return exactly this format:" not in model.prompt
    assert "do not output reasoning" in model.prompt
    assert "The response must start with SELECT." in model.prompt
    assert result["current_thought"] == ""
    assert result["generated_query"] == "SELECT count(*) FROM singer;"
