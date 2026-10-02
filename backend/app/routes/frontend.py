"""Serves the production build of the React app, when present."""

from pathlib import Path

from flask import Blueprint, current_app, send_from_directory

bp = Blueprint("frontend", __name__)


@bp.get("/")
def index():
    static_dir = Path(current_app.static_folder)
    if not (static_dir / "index.html").exists():
        return "The 'dist' folder does not exist. Run 'npm run build' in the frontend first.", 404
    return send_from_directory(static_dir, "index.html")
