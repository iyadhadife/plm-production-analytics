"""Orchestration of a chatbot question: prompt, generation, execution, formatting."""

from pathlib import Path

from app.chat.dataframes import describe, load_excel_files
from app.chat.executor import run_generated_code
from app.chat.formatting import format_result
from app.chat.gemini import CodeGenerator, is_valid_python
from app.chat.prompts import MAIN_PROMPT, STRICT_PROMPT


def answer_question(question: str, folder: Path, generator: CodeGenerator) -> dict:
    """Return {'answer': str, 'code': str | None, 'error': bool}."""
    frames = load_excel_files(folder)
    if not frames:
        return {"answer": "No Excel file is available. Please upload .xlsx files first.", "code": None, "error": True}

    data = describe(frames)
    code = generator.generate(MAIN_PROMPT.format(data=data, question=question))
    if not is_valid_python(code):
        # retry once with a stricter prompt
        code = generator.generate(STRICT_PROMPT.format(data=data, question=question))
        if not is_valid_python(code):
            return {"answer": "❌ The generated code has syntax errors. Please rephrase your question more simply.",
                    "code": code, "error": True}

    try:
        result = run_generated_code(code, frames)
    except Exception as exc:
        return {"answer": f"Error while running the code: {exc}", "code": code, "error": True}
    return {"answer": format_result(result), "code": code, "error": False}
