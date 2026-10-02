"""Loading (with an in-memory cache) and description of the uploaded Excel files."""

from pathlib import Path

import pandas as pd

_cache: dict[str, pd.DataFrame] = {}


def load_excel_files(folder: Path) -> dict[str, pd.DataFrame]:
    frames = {}
    for path in sorted(Path(folder).glob("*.xls*")):
        if path.name not in _cache:
            try:
                _cache[path.name] = pd.read_excel(path)
            except Exception:  # skip unreadable / corrupted files
                continue
        frames[path.name] = _cache[path.name]
    return frames


def describe(frames: dict[str, pd.DataFrame]) -> str:
    """Text description of every DataFrame for the prompt."""
    parts = []
    for name, df in frames.items():
        parts.append(
            f"\n📊 File: {name}\n"
            f"   - Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
            f"   - Columns: {', '.join(map(str, df.columns))}\n"
            f"   - Types: { {c: str(t) for c, t in df.dtypes.items()} }\n"
            f"   - Sample (first 3 rows):\n{df.head(3).to_dict('records')}\n"
        )
    return "".join(parts)
