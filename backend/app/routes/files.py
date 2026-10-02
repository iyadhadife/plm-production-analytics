"""Upload, listing, download and table preview of the source files."""

from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from app.processing.loader import read_excel
from app.reports.excel_table import render_excel_table
from app.routes.responses import error, html_response

bp = Blueprint("files", __name__)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def _upload_dir() -> Path:
    return Path(current_app.config["UPLOAD_DIR"])


def _is_allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@bp.get("/api/files")
def list_files():
    files = [
        {
            "id": path.name,
            "name": path.name,
            "type": "image/jpeg" if path.name.lower().endswith(IMAGE_EXTENSIONS) else "application/octet-stream",
            "size": f"{path.stat().st_size / 1024:.2f} KB",
            "url": f"/uploads/{path.name}",
        }
        for path in sorted(_upload_dir().iterdir())
        if path.is_file() and not path.name.startswith(".")
    ]
    return jsonify(files)


@bp.post("/api/upload")
def upload_file():
    file = request.files.get("file")
    if file is None:
        return error('No file in the request (missing "file" field)')
    if file.filename == "":
        return error("Empty file name")
    if not _is_allowed(file.filename):
        return error("File type not allowed")

    filename = secure_filename(file.filename)
    file.save(_upload_dir() / filename)
    return jsonify({"message": "File uploaded", "filename": filename, "url": f"/uploads/{filename}"}), 201


@bp.get("/uploads/<path:filename>")
def download_file(filename):
    return send_from_directory(_upload_dir(), filename)


@bp.get("/api/files/<filename>/table")
def excel_table(filename):
    filename = secure_filename(filename)
    if not filename.endswith(".xlsx"):
        return error("Only .xlsx files are supported")
    path = _upload_dir() / filename
    if not path.exists():
        return error("File not found", 404)
    return html_response(render_excel_table(read_excel(path), filename))
