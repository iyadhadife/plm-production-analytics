"""Reading of the three source Excel files."""

from pathlib import Path

import pandas as pd
from flask import current_app

from app.config import Config


def read_excel(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.replace("\xa0", " ", regex=False)
    return df


def source_paths(folder: Path | None = None) -> tuple[Path, Path, Path]:
    folder = Path(folder) if folder else _upload_dir()
    return folder / Config.MES_FILE, folder / Config.PLM_FILE, folder / Config.ERP_FILE


def load_sources(folder: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return the (mes, plm, erp) DataFrames."""
    mes_path, plm_path, erp_path = source_paths(folder)
    return read_excel(mes_path), read_excel(plm_path), read_excel(erp_path)


def _upload_dir() -> Path:
    try:
        return Path(current_app.config["UPLOAD_DIR"])
    except RuntimeError:  # outside a Flask request (scripts, tests)
        return Config.UPLOAD_DIR
