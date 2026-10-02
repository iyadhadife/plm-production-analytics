"""Response helpers shared by the routes."""

from flask import jsonify

HTML = {"Content-Type": "text/html; charset=utf-8"}


def html_response(body: str):
    return body, 200, HTML


def error(message: str, status: int = 400):
    return jsonify({"error": message}), status
