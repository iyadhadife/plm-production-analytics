"""Plotly layout defaults and marker sizing."""

import numpy as np
import pandas as pd

from app.analytics.constants import COLORS as C


def layout(**overrides) -> dict:
    """Base Plotly layout; dict overrides are merged one level deep."""
    base = {
        "paper_bgcolor": C["surface"],
        "plot_bgcolor": C["surface"],
        "font": {"family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif",
                 "size": 12, "color": C["text2"]},
        "margin": {"l": 60, "r": 24, "t": 16, "b": 48},
        "hoverlabel": {"bgcolor": "#ffffff", "bordercolor": C["border"], "font": {"color": C["text"]}},
        "xaxis": {"gridcolor": C["grid"], "zerolinecolor": C["border"], "linecolor": C["border"]},
        "yaxis": {"gridcolor": C["grid"], "zerolinecolor": C["border"], "linecolor": C["border"]},
        "legend": {"orientation": "h", "y": 1.08, "x": 0, "font": {"color": C["text2"]}},
        "showlegend": False,
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = {**base[key], **value}
        else:
            base[key] = value
    return base


def bubble_sizes(values, max_px: float = 46) -> tuple[list[float], float]:
    """Marker sizes and the matching Plotly `sizeref` for area-scaled bubbles."""
    v = np.asarray(pd.Series(values).fillna(0).clip(lower=0), dtype=float)
    ref = 2.0 * (v.max() or 1) / (max_px ** 2)
    return v.tolist(), ref


BAR_LINE = {"color": C["surface"], "width": 2}
