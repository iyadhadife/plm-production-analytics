from app.chat.formatting import format_result
from app.chat.gemini import strip_markdown
from app.chat.service import answer_question
from app.config import Config


class FakeGenerator:
    def __init__(self, code):
        self.code = code

    def generate(self, prompt):
        return self.code


def test_answer_runs_generated_code():
    code = 'result = f"{len(dataframes)} files"'
    answer = answer_question("how many files?", Config.UPLOAD_DIR, FakeGenerator(code))
    assert answer == {"answer": "3 files", "code": code, "error": False}


def test_invalid_code_is_reported():
    answer = answer_question("?", Config.UPLOAD_DIR, FakeGenerator("result = ("))
    assert answer["error"] is True


def test_strip_markdown():
    assert strip_markdown("```python\nresult = 1\n```") == "result = 1"


def test_format_list_of_dicts():
    assert format_result([{"a": 1000}]) == "✅ Found 1 result(s):\n\n1. a: 1,000"
