"""HTTP routes, grouped by feature."""

from flask import Flask

from app.routes import analyses, chat, files, frontend, reports


def register_blueprints(app: Flask) -> None:
    for module in (frontend, files, reports, analyses, chat):
        app.register_blueprint(module.bp)
