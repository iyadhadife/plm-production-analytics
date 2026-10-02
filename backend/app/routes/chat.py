"""Chatbot endpoint: POST /api/chat {"question": "..."}."""

from functools import lru_cache
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from app.chat import answer_question
from app.chat.gemini import CodeGenerator

bp = Blueprint("chat", __name__)


@lru_cache(maxsize=1)
def _generator(api_key: str | None, model: str) -> CodeGenerator:
    return CodeGenerator(api_key, model)


@bp.post("/api/chat")
def chat():
    question = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        generator = _generator(current_app.config["GEMINI_API_KEY"], current_app.config["GEMINI_MODEL"])
        return jsonify(answer_question(question, Path(current_app.config["UPLOAD_DIR"]), generator))
    except Exception as exc:
        return jsonify({"answer": f"Server error: {exc}", "error": True}), 500
