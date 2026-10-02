"""Cross analyses MES × PLM × ERP: /api/analyses/<name>."""

from flask import Blueprint, jsonify

from app.analytics import ANALYSES, render_analysis
from app.routes.responses import error, html_response

bp = Blueprint("analyses", __name__, url_prefix="/api/analyses")


@bp.get("")
def list_analyses():
    return jsonify(list(ANALYSES))


@bp.get("/<name>")
def analysis(name):
    if name not in ANALYSES:
        return error(f"Unknown analysis. Available: {', '.join(ANALYSES)}", 404)
    try:
        return html_response(render_analysis(name))
    except Exception as exc:
        return error(f"Analysis error: {exc}", 500)
