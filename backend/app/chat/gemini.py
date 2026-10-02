"""Thin wrapper around the Gemini API returning clean Python code."""

import google.generativeai as genai


class CodeGenerator:
    def __init__(self, api_key: str | None, model: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:
        return strip_markdown(self._model.generate_content(prompt).text)


def strip_markdown(text: str) -> str:
    """Remove ```python fences and normalise line endings."""
    code = text.strip()
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    return code.strip().replace("\r\n", "\n").replace("\r", "\n")


def is_valid_python(code: str) -> bool:
    try:
        compile(code, "<generated>", "exec")
        return True
    except SyntaxError:
        return False
