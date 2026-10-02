"""Flask application factory."""

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes import register_blueprints


def create_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__, static_folder=str(config.STATIC_DIR), static_url_path="")
    app.config.from_object(config)
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # The React dev server runs on another port, so allow cross-origin calls.
    CORS(app)
    register_blueprints(app)
    return app
